"""
AI 裁判服务 - 基于 MiniMax API
"""
import json
import os
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List
try:
    from backend.config import Config
    from backend.services.mtgch_api import MTGCHAPIClient
    from backend.services.log_service import log_info, log_warning, log_error, log_service
except ImportError:
    # 兼容本地测试环境（直接运行或测试时）
    try:
        from config import Config
    except ImportError:
        Config = None
    try:
        from services.mtgch_api import MTGCHAPIClient
    except ImportError:
        MTGCHAPIClient = None
    try:
        from services.log_service import log_info, log_warning, log_error, log_service
    except ImportError:
        def log_info(*args, **kwargs): pass
        def log_warning(*args, **kwargs): pass
        def log_error(*args, **kwargs): pass
        log_service = None


# 配置 AI 裁判专用日志
_ai_logger = None

# 云存储日志缓存
_log_buffer = []


def _upload_log_to_cloudStorage(log_content: str):
    """上传日志到云存储"""
    try:
        # 获取环境变量
        env_id = os.getenv("TCB_ENV_ID") or os.getenv("TENCENTCLOUD_APPID", "")
        secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
        secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")

        if not env_id or not secret_id or not secret_key:
            print(f"云存储配置缺失: env_id={env_id}, secret_id={secret_id is not None}, secret_key={secret_key is not None}")
            return False

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"ai_judge/logs/{timestamp}.log"

        # 使用静态网站托管的上传方式
        # 先尝试获取上传签名（简单方式：使用临时凭证）
        # 这里使用简化的方式：直接写入文件到静态托管

        # 由于云函数环境没有直接的云存储写入权限，
        # 我们使用 CloudBase CLI 的方式或者 HTTP API
        # 这里使用基础认证方式

        bucket = "6d61-magic-rules-assistant-0a1904c329-1410769303"

        # 使用 CDN 域名上传
        url = f"https://{bucket}.tcb.qcloud.la/{file_name}"

        # 生成简单的 Authorization（这里使用简化方式）
        # 实际生产环境应该使用完整的签名算法
        print(f"日志上传到: https://{bucket}.tcb.qcloud.la/{file_name}")
        print(f"日志内容长度: {len(log_content)} 字符")

        # 尝试使用云存储 HTTP API 上传
        # 这里先只打印日志路径，实际使用需要配置完整的上传签名
        return True

    except Exception as e:
        print(f"上传日志到云存储失败: {e}")
        return False


def _get_ai_logger():
    """获取或创建 AI 裁判日志记录器"""
    global _ai_logger

    # 检查是否在云函数环境中
    is_cloud = bool(os.getenv("SCF_FUNCTION_NAME") or os.getenv("TENCENTCLOUD_RUNENV"))

    # 如果已存在 logger，直接返回
    if _ai_logger is not None:
        return _ai_logger

    # 创建日志记录器
    logger = logging.getLogger("ai_judge")
    logger.setLevel(logging.INFO)

    # 云函数环境：只使用控制台 handler（stdout 会被云日志收集）
    if is_cloud:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logger.addHandler(console_handler)
        _ai_logger = logger
    else:
        # 本地环境：创建日志目录和文件
        try:
            log_dir = Config.LOG_DIR
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # AI 裁判专用日志文件
            ai_log_file = os.path.join(log_dir, f"ai_judge_{datetime.now().strftime('%Y%m%d')}.log")

            # 文件 handler
            file_handler = logging.FileHandler(ai_log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

            # 控制台 handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        except Exception:
            # 如果创建文件失败，只使用控制台
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            logger.addHandler(console_handler)

        _ai_logger = logger

    return _ai_logger


class AIJudgeService:
    """AI 裁判服务"""

    # 规则文件列表（相对于 base_dir）
    RULE_FILES = [
        "markdown/glossarycn.md",      # 中文词汇表
        "knowledge-map/triggered-abilities.md",  # 触发式异能
        "knowledge-map/stack-priority.md",       # 堆叠与优先权
        "knowledge-map/continuous-effects.md",    # 持续效应
        "knowledge-map/copy-effects.md",         # 复制效应
    ]

    def __init__(self):
        self.api_key = Config.MINIMAX_API_KEY
        self.model = Config.MINIMAX_MODEL
        self.base_url = Config.MINIMAX_BASE_URL
        self.conversation_history: Dict[str, List[Dict]] = {}  # 按用户会话维护历史

        # OpenCLAW Gateway 配置
        self.openclaw_enabled = Config.OPENCLAW_ENABLED
        self.openclaw_gateway_url = Config.OPENCLAW_GATEWAY_URL
        self.openclaw_gateway_token = Config.OPENCLAW_GATEWAY_TOKEN

        # 加载规则内容
        self.rules_content = self._load_rules()

        # 系统提示词
        self.system_prompt = self._build_system_prompt()

    def _is_cloud_function(self) -> bool:
        """检查是否在云函数环境中"""
        return bool(os.getenv("SCF_FUNCTION_NAME") or os.getenv("TENCENTCLOUD_RUNENV"))

    def _get_cloud_storage_url(self, file_path: str) -> Optional[str]:
        """
        获取云存储文件的临时下载链接
        使用 CloudBase HTTP API
        """
        env_id = os.getenv("TCB_ENV_ID")
        if not env_id:
            # 尝试从环境变量获取
            env_id = os.getenv("TENCENTCLOUD_APPID", "")

        if not env_id:
            # 从 SCF 相关信息中提取
            return None

        # 使用云存储的基础 URL 格式
        # 注意：需要在云存储控制台配置安全规则允许访问
        return f"https://cloudfile-{env_id}.tcb.qcloud.la/{file_path}"

    def _load_rules(self) -> str:
        """
        从云存储或本地加载规则内容
        """
        # 优先尝试从云存储加载
        if self._is_cloud_function():
            content = self._load_from_cloud_storage()
            if content:
                return content

        # 备选：从本地加载（用于开发/测试）
        local_path = os.getenv("AI_RULES_LOCAL_PATH", "/Users/lianghaoming/cbworkplace/.claude/skills/ai_judge/345")
        content = self._load_from_local(local_path)
        if content:
            return content

        print("未能加载规则内容，使用默认提示词")
        return ""

    def _load_from_cloud_storage(self) -> str:
        """从云存储加载规则"""
        print("尝试从云存储加载规则...")
        loaded_content = []

        # 获取环境ID
        env_id = os.getenv("TCB_ENV_ID") or os.getenv("TENCENTCLOUD_APPID", "")
        if not env_id:
            print("  未找到环境ID，跳过云存储加载")
            return ""

        # 云存储URL格式: https://{bucket}.tcb.qcloud.la/{path}
        # Bucket格式: 6d61-magic-rules-assistant-0a1904c329-1410769303
        bucket = "6d61-magic-rules-assistant-0a1904c329-1410769303"
        cloud_prefix = "ai_judge/345/"

        for file_path in self.RULE_FILES:
            try:
                # 使用 CDN 域名访问
                full_cloud_path = cloud_prefix + file_path
                url = f"https://{bucket}.tcb.qcloud.la/{full_cloud_path}"

                response = requests.get(url, timeout=10, headers={
                    "User-Agent": "mtgAsk/1.0"
                })

                if response.status_code == 200:
                    loaded_content.append(f"\n\n=== {file_path} ===\n\n")
                    loaded_content.append(response.text)
                    print(f"  ✓ 已加载: {file_path}")
                else:
                    print(f"  ✗ 无法获取: {file_path} (HTTP {response.status_code})")

            except Exception as e:
                print(f"  ✗ 加载失败 {file_path}: {e}")
                continue

        if loaded_content:
            content = "".join(loaded_content)
            print(f"共加载 {len(content)} 字符的规则内容")
            return content
        else:
            print("云存储加载失败")
            return ""

    def _load_from_local(self, local_path: str) -> str:
        """从本地加载规则"""
        import os

        print(f"尝试从本地加载规则: {local_path}")
        loaded_content = []

        # 如果 local_path 是绝对路径，直接使用
        if os.path.isabs(local_path):
            base_dir = local_path if os.path.isdir(local_path) else os.path.dirname(local_path)
        else:
            # 尝试相对路径
            base_dir = os.path.join(os.path.dirname(__file__), local_path)

        # 检查目录是否存在
        if not os.path.isdir(base_dir):
            # 尝试项目根目录
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".claude/skills/ai_judge/345")

        if not os.path.isdir(base_dir):
            print(f"  目录不存在: {base_dir}")
            return ""

        print(f"  使用目录: {base_dir}")

        for file_path in self.RULE_FILES:
            # 保持完整路径
            full_path = os.path.join(base_dir, file_path)

            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        loaded_content.append(f"\n\n=== {file_path} ===\n\n")
                        loaded_content.append(content)
                        print(f"  ✓ 已加载: {file_path}")
                except Exception as e:
                    print(f"  ✗ 读取失败 {file_path}: {e}")
            else:
                print(f"  - 文件不存在: {full_path}")

        if loaded_content:
            content = "".join(loaded_content)
            print(f"共加载 {len(content)} 字符的规则内容")
            return content

        return ""

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        base_prompt = """你是一位专业的万智牌裁判助手，精通万智牌 Comprehensive Rules（综合规则）。

## 你的职责
1. 回答玩家关于万智牌规则的问题
2. 分析对局情况，判断触发时机、费用支付、优先权等
3. 解释关键词异能和卡牌互动规则

## 回答规范
- 使用中文回答
- 引用具体的规则编号（如 CR 117.1、CR 504.1）
- 解释清晰，简明扼要
- 如果问题涉及多个规则，逐一说明

## 重要规则参考
- 堆叠（Stack）：咒语和异能在堆叠上 resolving
- 优先权（Priority）：谁可以做什么
- 触发式异能（Triggered Abilities）：何时触发、如何进入堆叠
- 伤害步骤（Combat Damage）：伤害如何分配

如果不确定某些细节，请明确说明并给出合理的推测。"""

        # 如果有加载的规则内容，附加到提示词中
        if self.rules_content:
            base_prompt += f"""

## 规则知识库（供参考）

{self.rules_content}

请在回答时参考上述规则内容。"""

        return base_prompt

    def _query_card(self, card_name: str) -> Optional[Dict]:
        """
        使用 mtgch API 查询卡牌信息

        Args:
            card_name: 卡牌名称

        Returns:
            卡牌信息字典，包含 name, type_line, oracle_text 等
        """
        logger = _get_ai_logger()

        try:
            # 使用已有的 MTGCH API 客户端
            client = MTGCHAPIClient()
            result = client.search_cards(card_name, page_size=1)

            if result.get("items") and len(result["items"]) > 0:
                card = result["items"][0]
                logger.info(f"查询到卡牌: {card.get('name', card_name)}")

                # 提取关键信息
                return {
                    "name": card.get("name", card_name),
                    "type_line": card.get("type_line", ""),
                    "oracle_text": card.get("oracle_text", ""),
                    "mana_cost": card.get("mana_cost", ""),
                    "power": card.get("power"),
                    "toughness": card.get("toughness"),
                    "colors": card.get("colors", []),
                }
            logger.warning(f"未找到卡牌: {card_name}")
            return None
        except Exception as e:
            logger.error(f"查询卡牌失败: {card_name}, 错误: {e}")
            return None

    def _call_api(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """调用 MiniMax API"""
        # 使用 print 确保日志输出到云日志
        print(f"=== MiniMax API 请求 ===")
        print(f"Model: {self.model}")
        print(f"Temperature: {temperature}")
        # 只记录前3条消息（避免过长）
        for i, msg in enumerate(messages[:3]):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            # 截断过长的内容
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"Message {i} [{role}]: {content}")
        if len(messages) > 3:
            print(f"... 共 {len(messages)} 条消息")

        if not self.api_key:
            print("ERROR: No API key configured")
            return None

        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            print(f"Calling MiniMax API: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            print(f"Response Status: {response.status_code}")

            response.raise_for_status()
            result = response.json()

            # 记录完整响应（用于调试）
            print(f"=== MiniMax API 响应 ===")
            print(f"Response Keys: {list(result.keys())}")

            if "usage" in result:
                print(f"Usage: {result['usage']}")

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                # 记录回复内容摘要
                print(f"回复内容长度: {len(content)} 字符")
                print(f"回复内容前200字: {content[:200]}...")
                return content
            print("No choices in response")
            return None
        except Exception as e:
            print(f"MiniMax API 调用失败: {e}")
            return None

    def _call_openclaw_gateway(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """调用 OpenCLAW Gateway HTTP API"""
        print(f"=== OpenCLAW HTTP 请求 ===")
        print(f"Enabled: {self.openclaw_enabled}")
        print(f"Gateway URL: {self.openclaw_gateway_url}")

        if not self.openclaw_enabled:
            print("OpenCLAW 未启用")
            return None

        # 从 messages 中提取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            print("未找到用户消息")
            return None

        url = f"{self.openclaw_gateway_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        # 如果有 token 则添加认证头
        if self.openclaw_gateway_token:
            headers["Authorization"] = f"Bearer {self.openclaw_gateway_token}"

        # 构建消息（只保留 system 和最新的 user 消息）
        http_messages = []
        for msg in messages:
            if msg.get("role") in ["system", "user", "assistant"]:
                http_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        payload = {
            "model": "openclaw",
            "messages": http_messages,
            "temperature": temperature
        }

        try:
            print(f"Calling OpenCLAW Gateway: {url}")
            print(f"User message: {user_message[:100]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            print(f"Response Status: {response.status_code}")

            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}, {response.text[:200]}")
                return None

            result = response.json()
            print(f"Response Keys: {list(result.keys())}")

            # 提取回复内容 - OpenAI 兼容格式
            content = ""
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")

            if content:
                print(f"回复内容长度: {len(content)} 字符")
                print(f"回复内容前200字: {content[:200]}...")
                return content

            # 如果没有标准字段，打印完整响应以便调试
            print(f"完整响应: {json.dumps(result, ensure_ascii=False)[:500]}...")
            return None

        except Exception as e:
            print(f"OpenCLAW HTTP 调用失败: {e}")
            return None
                return None

            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {e}")
                print(f"原始输出: {result.stdout[:500]}")
                return None

        except subprocess.TimeoutExpired:
            print("OpenCLAW CLI 执行超时")
            return None
        except FileNotFoundError:
            print("未找到 openclaw 命令，请确保已安装 OpenCLAW")
            return None
        except Exception as e:
            print(f"OpenCLAW CLI 调用失败: {e}")
            return None

    def _call_stream_api(self, messages: List[Dict], temperature: float = 0.7):
        """
        调用 MiniMax API 流式响应
        返回生成器，逐步 yield 内容
        """
        print(f"=== MiniMax 流式 API 请求 ===")
        print(f"Model: {self.model}")
        print(f"Temperature: {temperature}")

        if not self.api_key:
            print("ERROR: No API key configured")
            yield {"error": "API key not configured"}
            return

        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        try:
            print(f"Calling MiniMax Streaming API: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=60, stream=True)
            print(f"Response Status: {response.status_code}")

            if response.status_code != 200:
                yield {"error": f"API error: {response.status_code}"}
                return

            # 流式读取响应
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    # MiniMax 流式响应格式: data: {"choices":[{"delta":{"content":"xxx"}}]}
                    if line.startswith('data: '):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]
                                    yield {"content": content}
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"MiniMax 流式 API 调用失败: {e}")
            yield {"error": str(e)}

    def _extract_card_names(self, text: str) -> List[str]:
        """
        从文本中提取可能的卡牌名称
        检测引号、书名号、常见卡牌提及方式
        """
        import re

        card_names = []

        # 匹配中文引号、书名号等包围的卡牌名
        patterns = [
            r'「([^」]+)」',      # 日式引号
            r'『([^』]+)』',      # 日式双引号
            r'"([^"]+)"',         # 英文引号
            r'《([^》]+)》',      # 书名号
            r'【([^】]+)】',      # 方括号
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            card_names.extend(matches)

        # 如果没有找到引号包围的名称，尝试提取常见的中文卡牌名
        # 万智牌中文名称通常是 2-6 个汉字
        if not card_names:
            # 常见单字卡牌名称
            common_cards = ['闪电击', '火球', '去除', '反击', '变脸', '抹消', '沉思', '体验']
            for card in common_cards:
                if card in text:
                    card_names.append(card)

        return card_names

    def _enhance_message_with_cards(self, user_message: str) -> str:
        """
        检测用户消息中的卡牌名称并查询，附加卡牌信息
        """
        logger = _get_ai_logger()

        # 提取可能的卡牌名称
        card_names = self._extract_card_names(user_message)

        if not card_names:
            return user_message

        # 查询每个卡牌
        card_info_list = []
        for card_name in card_names:
            card = self._query_card(card_name)
            if card:
                card_info = f"【{card['name']}】{card['type_line']} - {card['oracle_text']}"
                if card.get('mana_cost'):
                    card_info += f" | 费用: {card['mana_cost']}"
                if card.get('power') and card.get('toughness'):
                    card_info += f" | P/T: {card['power']}/{card['toughness']}"
                card_info_list.append(card_info)
                logger.info(f"自动查询卡牌: {card['name']}")

        # 如果找到卡牌信息，附加到用户消息
        if card_info_list:
            enhanced = user_message + "\n\n--- 自动查询的相关卡牌信息 ---\n" + "\n".join(card_info_list)
            logger.info(f"已自动查询 {len(card_info_list)} 张卡牌")
            return enhanced

        return user_message

    def chat(self, user_message: str, session_id: str = "default") -> Dict:
        """
        与 AI 裁判对话

        Args:
            user_message: 用户消息
            session_id: 会话ID，用于维护对话历史

        Returns:
            {"success": bool, "reply": str}
        """
        logger = _get_ai_logger()

        # 记录用户提问
        logger.info(f"=== 会话 [{session_id}] 用户提问 ===\n{user_message}")

        # 自动检测并查询卡牌信息
        enhanced_message = self._enhance_message_with_cards(user_message)

        # 获取或初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]

        history = self.conversation_history[session_id]

        # 添加用户消息（增强版）
        history.append({"role": "user", "content": enhanced_message})

        # 构建调试信息
        debug_info = {
            "session_id": session_id,
            "user_message": user_message,
            "enhanced_message": enhanced_message[:500] + "..." if len(enhanced_message) > 500 else enhanced_message,
            "message_count": len(history),
            "card_query_performed": enhanced_message != user_message
        }

        # 调用 API（优先使用 OpenCLAW Gateway）
        reply = None
        if self.openclaw_enabled:
            print("尝试调用 OpenCLAW Gateway...")
            reply = self._call_openclaw_gateway(history)
            if reply:
                print("OpenCLAW Gateway 调用成功")

        # 如果 OpenCLAW 失败，返回错误
        if not reply:
            logger.error(f"会话 [{session_id}] OpenCLAW 调用失败")
            return {
                "success": False,
                "reply": "AI 裁判暂时无法回答，请稍后再试。",
                "debug": debug_info
            }

        if reply:
            # 添加助手回复到历史
            history.append({"role": "assistant", "content": reply})

            # 记录 AI 回复
            logger.info(f"=== 会话 [{session_id}] AI 回复 ===\n{reply}")

            # 使用统一日志服务记录（会同时保存到本地和云存储）
            log_info("ai_judge", f"会话 [{session_id}] 用户提问", {
                "message": user_message[:200],
                "session_id": session_id
            })
            log_info("ai_judge", f"会话 [{session_id}] AI 回复", {
                "reply_length": len(reply),
                "reply_preview": reply[:200]
            })

            # 限制历史长度（保留 system + 最近10轮对话）
            if len(history) > 21:
                self.conversation_history[session_id] = [history[0]] + history[-20:]

            return {
                "success": True,
                "reply": reply,
                "debug": debug_info
            }
        else:
            logger.error(f"会话 [{session_id}] API 调用失败")
            log_error("ai_judge", f"会话 [{session_id}] API 调用失败", {
                "message": user_message[:200]
            })
            return {
                "success": False,
                "reply": "AI 裁判暂时无法回答，请稍后再试。",
                "debug": debug_info
            }

    def analyze(self, request_data: Dict) -> Dict:
        """
        分析对局状态

        Args:
            request_data: 包含 game_state, cards, actions 等

        Returns:
            {"success": bool, "analysis": str}
        """
        logger = _get_ai_logger()

        game_state = request_data.get("game_state", "")
        cards = request_data.get("cards", [])
        question = request_data.get("question", "")

        # 记录分析请求
        logger.info(f"=== 对局分析请求 ===\n对局: {game_state}\n卡牌: {cards}\n问题: {question}")

        # 构建分析请求
        analysis_prompt = f"""请分析以下对局情况：

**对局描述：**
{game_state}

**相关卡牌：**
{chr(10).join([f"- {card}" for card in cards]) if cards else "无"}

**问题：**
{question}

请根据万智牌规则进行分析。"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]

        # 调用 API（优先使用 OpenCLAW Gateway）
        result = None
        if self.openclaw_enabled:
            print("分析请求：尝试调用 OpenCLAW Gateway...")
            result = self._call_openclaw_gateway(messages, temperature=0.5)
            if result:
                print("OpenCLAW Gateway 分析成功")

        # 如果 OpenCLAW 失败，返回错误
        if not result:
            logger.error("对局分析失败：OpenCLAW 调用失败")
            return {
                "success": False,
                "analysis": "AI 裁判暂时无法分析，请稍后再试。"
            }

        if result:
            logger.info(f"=== 对局分析结果 ===\n{result}")
            return {
                "success": True,
                "analysis": result
            }
        else:
            logger.error("对局分析 API 调用失败")
            return {
                "success": False,
                "analysis": "分析失败，请稍后再试。"
            }

    def stream_chat(self, user_message: str, session_id: str = "default"):
        """
        与 AI 裁判对话 - 流式版本
        返回生成器，逐步 yield 内容片段

        Args:
            user_message: 用户消息
            session_id: 会话ID，用于维护对话历史

        Yields:
            {"content": str} - 内容片段
            {"done": bool} - 完成信号
            {"error": str} - 错误信息
        """
        logger = _get_ai_logger()

        # 记录用户提问
        logger.info(f"=== 会话 [{session_id}] 流式提问 ===\n{user_message}")

        if not self.api_key:
            logger.error("AI 裁判 API Key 未配置")
            yield {"error": "AI 裁判服务暂未配置，请联系管理员。"}
            return

        # 自动检测并查询卡牌信息
        enhanced_message = self._enhance_message_with_cards(user_message)

        # 获取或初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]

        history = self.conversation_history[session_id]

        # 添加用户消息（增强版）
        history.append({"role": "user", "content": enhanced_message})

        # 流式调用 API
        full_reply = ""
        try:
            for chunk in self._call_stream_api(history):
                if "error" in chunk:
                    logger.error(f"流式 API 错误: {chunk['error']}")
                    yield chunk
                    return
                if "content" in chunk:
                    content = chunk["content"]
                    full_reply += content
                    yield {"content": content}
        except Exception as e:
            logger.error(f"流式对话异常: {e}")
            yield {"error": str(e)}
            return

        # 添加助手回复到历史
        history.append({"role": "assistant", "content": full_reply})

        # 限制历史长度（保留 system + 最近 20 条）
        if len(history) > 21:
            self.conversation_history[session_id] = [history[0]] + history[-20:]

        logger.info(f"=== 会话 [{session_id}] 流式回复完成 ===")
        yield {"done": True}

    def clear_session(self, session_id: str = "default"):
        """清除会话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# 全局实例
ai_judge_service = AIJudgeService()
