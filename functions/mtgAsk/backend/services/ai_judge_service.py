"""
AI 裁判服务 - 基于 MiniMax API
"""
import json
import os
import requests
from typing import Dict, Optional, List
from config import Config


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

    def _call_api(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """调用 MiniMax API"""
        if not self.api_key:
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
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            print(f"MiniMax API 调用失败: {e}")
            return None

    def chat(self, user_message: str, session_id: str = "default") -> Dict:
        """
        与 AI 裁判对话

        Args:
            user_message: 用户消息
            session_id: 会话ID，用于维护对话历史

        Returns:
            {"success": bool, "reply": str}
        """
        if not self.api_key:
            return {
                "success": False,
                "reply": "AI 裁判服务暂未配置，请联系管理员。"
            }

        # 获取或初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]

        history = self.conversation_history[session_id]

        # 添加用户消息
        history.append({"role": "user", "content": user_message})

        # 调用 API
        reply = self._call_api(history)

        if reply:
            # 添加助手回复到历史
            history.append({"role": "assistant", "content": reply})

            # 限制历史长度（保留 system + 最近10轮对话）
            if len(history) > 21:
                self.conversation_history[session_id] = [history[0]] + history[-20:]

            return {
                "success": True,
                "reply": reply
            }
        else:
            return {
                "success": False,
                "reply": "AI 裁判暂时无法回答，请稍后再试。"
            }

    def analyze(self, request_data: Dict) -> Dict:
        """
        分析对局状态

        Args:
            request_data: 包含 game_state, cards, actions 等

        Returns:
            {"success": bool, "analysis": str}
        """
        if not self.api_key:
            return {
                "success": False,
                "analysis": "AI 裁判服务暂未配置。"
            }

        game_state = request_data.get("game_state", "")
        cards = request_data.get("cards", [])
        question = request_data.get("question", "")

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

        result = self._call_api(messages, temperature=0.5)

        if result:
            return {
                "success": True,
                "analysis": result
            }
        else:
            return {
                "success": False,
                "analysis": "分析失败，请稍后再试。"
            }

    def clear_session(self, session_id: str = "default"):
        """清除会话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# 全局实例
ai_judge_service = AIJudgeService()
