"""
AI 裁判服务 - 基于 MiniMax API
"""
import json
import os
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List
import paramiko
try:
    from backend.config import Config
    from backend.services.mtgch_api import MTGCHAPIClient
    from backend.services.log_service import log_info, log_warning, log_error, log_service
    from backend.services.openclaw_client import OpenCLAWClient
    from backend.services.agent_pool_manager import AgentPoolManager
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
    try:
        from services.openclaw_client import OpenCLAWClient
    except ImportError:
        OpenCLAWClient = None
    try:
        from services.agent_pool_manager import AgentPoolManager
    except ImportError:
        AgentPoolManager = None


# 配置 AI 裁判专用日志
_ai_logger = None

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

    # 规则文件列表（相对于 magic-comp-rules-zh-cn-agent 目录）
    RULE_FILES = [
        "markdown/glossarycn.md",      # 中文词汇表
        "markdown/glossary.md",         # 英文词汇表
        "references/triggered-abilities.md",  # 触发式异能
        "references/stack-priority.md",       # 堆叠与优先权
        "references/continuous-effects.md",    # 持续效应
        "references/copy-effects.md",         # 复制效应
        "references/prevention-effects.md",   # 防止效应
        "references/replacement-effects.md",  # 替代式效应
    ]

    def __init__(self):
        self.api_key = Config.MINIMAX_API_KEY
        self.model = Config.MINIMAX_MODEL
        self.base_url = Config.MINIMAX_BASE_URL
        self.conversation_history: Dict[str, List[Dict]] = {}  # 按用户会话维护历史

        # 请求限流：记录每个用户的最后请求时间（秒）
        self._last_request_time: Dict[str, float] = {}
        self._rate_limit_seconds = 60  # 同一用户60秒内只能请求一次

        # OpenCLAW Gateway 配置
        self.openclaw_enabled = Config.OPENCLAW_ENABLED
        self.openclaw_host = Config.OPENCLAW_HOST
        self.openclaw_port = Config.OPENCLAW_PORT
        self.openclaw_ssh_user = Config.OPENCLAW_SSH_USER
        self.openclaw_ssh_password = Config.OPENCLAW_SSH_PASSWORD
        self.openclaw_ssh_key = Config.OPENCLAW_SSH_KEY
        self.openclaw_ssh_key_content = Config.OPENCLAW_SSH_KEY_CONTENT
        self.openclaw_agent = Config.OPENCLAW_AGENT

        # Mock 模式
        self.mock_mode = Config.OPENCLAW_MOCK

        # Agent 池管理器（用于 per-user agent）
        self.agent_pool = None
        if AgentPoolManager and self.openclaw_enabled:
            try:
                self.agent_pool = AgentPoolManager()
                print(f"AgentPoolManager 初始化成功: {self.agent_pool.get_pool_stats()}")
            except Exception as e:
                print(f"AgentPoolManager 初始化失败: {e}")

        # 加载规则内容
        self.rules_content = self._load_rules()

        # 系统提示词
        self.system_prompt = self._build_system_prompt()

    def _is_cloud_function(self) -> bool:
        """检查是否在云函数环境中"""
        return bool(os.getenv("SCF_FUNCTION_NAME") or os.getenv("TENCENTCLOUD_RUNENV"))

    def _load_rules(self) -> str:
        """
        从本地加载规则内容

        规则知识库通过 sync_judge_knowledge.py 同步到 OpenCLAW Gateway 服务器，
        由 OpenCLAW Agent 通过 ai-judge skill 读取。
        """
        # 从本地加载（用于开发/测试或备用）
        local_path = os.getenv("AI_RULES_LOCAL_PATH", "/Users/lianghaoming/cbworkplace/functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent")
        content = self._load_from_local(local_path)
        if content:
            return content

        print("未能加载规则内容，使用默认提示词")
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

    def _get_short_system_prompt(self) -> str:
        """构建简短版系统提示词（减少 token 消耗）"""
        return """你是一位专业的万智牌裁判。请简洁回答万智牌规则问题。

要求：
- 使用中文回答
- 简洁明了
- 引用规则编号

回答格式：先给出结论，再简要解释。"""

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

    def _call_openclaw_gateway(self, messages: List[Dict], agent_name: str = None, temperature: float = 0.7) -> Optional[str]:
        """调用 OpenCLAW Gateway CLI（通过 SSH）

        Args:
            messages: 对话历史
            agent_name: 可选，指定使用的 agent 名称（per-user agent）
            temperature: 温度参数（未使用，保留兼容性）
        """
        # 如果没有指定 agent_name，使用默认的
        effective_agent = agent_name or self.openclaw_agent

        print(f"=== OpenCLAW CLI 请求 ===")
        print(f"Enabled: {self.openclaw_enabled}")
        print(f"Host: {self.openclaw_host}:{self.openclaw_port}")
        print(f"Agent: {effective_agent}")
        print(f"Mock Mode: {self.mock_mode}")

        if self.mock_mode:
            print("Mock 模式：返回预设响应")
            return self._get_mock_response(messages)

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

        # 使用 OpenCLAWClient 调用
        if OpenCLAWClient:
            try:
                client = OpenCLAWClient(
                    host=self.openclaw_host,
                    port=self.openclaw_port,
                    username=self.openclaw_ssh_user,
                    password=self.openclaw_ssh_password,
                    key_content=self.openclaw_ssh_key_content,
                    agent=effective_agent
                )

                # 直接调用，返回纯文本
                content = client.call_agent(user_message)
                client.close()

                if content:
                    print(f"回复内容长度: {len(content)} 字符")
                    print(f"回复内容前200字: {content[:200]}...")
                    return content
                else:
                    print("未获取到回复内容，fallback 到 mock 模式")
                    return self._get_mock_response(messages)

            except Exception as e:
                print(f"OpenCLAW SSH 调用失败: {e}，fallback 到 mock 模式")
                return self._get_mock_response(messages)
        else:
            # 兼容：使用原有的 paramiko 实现
            return self._call_openclaw_gateway_legacy(messages, temperature)

    def _call_openclaw_gateway_legacy(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """调用 OpenCLAW Gateway CLI（通过 SSH）- 原有实现"""
        # 从 messages 中提取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            print("未找到用户消息")
            return None

        try:
            # 构建 CLI 命令
            # 使用 bash -i 来加载环境变量
            escaped_message = user_message.replace('"', '\\"')
            cmd = f'bash -i -c "openclaw agent --agent {self.openclaw_agent} -m \\"{escaped_message}\\" --json"'

            print(f"Executing: {cmd[:100]}...")

            # SSH 连接并执行
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 使用密钥或密码连接
            if self.openclaw_ssh_key:
                client.connect(
                    self.openclaw_host,
                    username=self.openclaw_ssh_user,
                    key_filename=self.openclaw_ssh_key,
                    timeout=30
                )
            elif self.openclaw_ssh_password:
                client.connect(
                    self.openclaw_host,
                    username=self.openclaw_ssh_user,
                    password=self.openclaw_ssh_password,
                    timeout=30
                )
            else:
                print("未配置 SSH 密钥或密码")
                return None

            stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
            output = stdout.read().decode()
            error = stderr.read().decode()

            client.close()

            if error and "bash: cannot set terminal" not in error:
                print(f"STDERR: {error[:200]}")

            # 解析 JSON 响应
            try:
                result = json.loads(output)
                if result.get("status") == "ok":
                    payloads = result.get("result", {}).get("payloads", [])
                    if payloads:
                        content = payloads[0].get("text", "")
                        print(f"回复内容长度: {len(content)} 字符")
                        print(f"回复内容前200字: {content[:200]}...")
                        return content

                print(f"API 返回错误: {result}，fallback 到 mock 模式")
                return self._get_mock_response(messages)

            except json.JSONDecodeError:
                print(f"JSON 解析失败，原始输出: {output[:500]}，fallback 到 mock 模式")
                return self._get_mock_response(messages)

        except Exception as e:
            print(f"OpenCLAW SSH 调用失败: {e}，fallback 到 mock 模式")
            return self._get_mock_response(messages)

    def _get_mock_response(self, messages: List[Dict]) -> str:
        """获取 Mock 响应（用于测试/服务器不可用时）"""
        # 从消息中提取用户问题
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # 简单的关键词匹配响应（Markdown 格式）
        user_lower = user_message.lower()

        # 预设响应模板（Markdown 格式）
        responses = {
            "default": """## ⚠️ Mock 响应模式

这是一条模拟回复，当前 AI 裁判服务不可用（服务器连接失败或维护中）。

---

### 您的问题
>{question}

---

### 模拟回复内容

**克撒传 (Urza's Saga)** 和 **红月 (Blood Moon)** 的互动涉及**层系统 (613)**：

---

### 牌张信息

| 牌 | 类型 | 关键异能的 |
|---|---|---|
| **克撒传** | 结界地 ~ 克撒的 | 传奇结界地，进场时有学问指示物，I产费，II造0/0机器人，III找0/1费神器 |
| **红月** | 结界 | 非基本地成为 Mountains |

---

### 互动分析

1. **红月**的效应是「非基本地成为 Mountains」—— 这是**类别改变 (layer 4)**
2. **克撒传**本身是一张「结界地」，属于**非基本地**（传奇地都不是基本地）
3. 因此，红月结算后，克撒传会**失去「结界地」类别，变成一座 Mountain**

---

### 结果

- 克撒传变成 Mountain 后，不再是结界
- 它作为 Saga 的III异能**不再生效**（因为不再是结界地）
- 它产无色费的异能（I）也失效
- 它变成红 Mountain，所以仍然能产R（因为Mountain产R）

---

### 总结

> 红月会让克撒传变成红月山脉，丧失所有结界/ Saga 异能，只保留产红费的 ability。

---

*此为 Mock 回复，生产环境请确保 OpenCLAW 服务器正常运行。*""",

            "克撒传": """## 克撒传 (Urza's Saga)

**类型**: 结界 ~ 地克撒的 (传奇地)

**费用**: {G/P}{G/P}{G/P}

**异 能**:

- **进场** — 克撒传进战场时，上面有若干个学问指示物。其数量等于你本回合中抓的牌数量减去一。
- **{T}**：加 **{C}**。
- **{P}**，移除克撒传上的一个学问指示物：派出一个 0/0，名为 konstrukt 的机械衍生物，然后你可以在其上放置一个 +1/+1 指示物，或两个 +1/+1 指示物（若你操控巨械）。若移除两个学问指示物，则改为派出一个 0/0 构造物。
- **{P}**，横置**：将一张神器牌从你的牌库顶放逐。若该牌是神器，则你可以施放该牌，且如果该牌是武具，则你可以将它装备在所派出的 konstrukt 上。

---

## 与红月 (Blood Moon) 的互动

### 层系统分析 (613.1)

| 层 | 效应 |
|----|------|
| 4 | 红月：将非基本地变为 Mountain |
| 6 | 克撒传：+1/+1 指示物（通过章节III） |

### 结论

红月结算后：
- 克撒传失去「地」类别 → 失去「结界地」类别
- 失去「Saga」超类别 → 所有章节异能失效
- 变成 Mountain → 只能产 {R}

**最终状态：红 Mountain，产 R，无任何结界/ Saga 异能**""",

            "红月": """## 红月 (Blood Moon)

**类型**: 结界

**费用**: {2}{R}{R}

**异 能**:

- 只要红月是横置的，所有非地永久物便额外具有 Mountain 地类别。
- 所有非基本地失去所有地类别，成为 Mountains。

---

## 与克撒传的互动

### 层系统 (613.1)

红月属于 **Layer 4**（类别改变层），在所有其他效应之后生效。

### 互动结果

| 状态 | 克撒传 |
|------|--------|
| 红月结算前 | 传奇结界地 ~ Saga，进场产 {C} |
| 红月结算后 | Mountain（失去地类别） |

### 关键规则

- **305.7**: 如果一张牌获得或失去地类别，它不再具有之前的地类别
- **713.1**: 红月结算时，所有非基本地成为 Mountains

---

**结论**: 红月会让克撒传变成普通的红 Mountain，丧失所有特殊能力。""",

            "闪电击": """## 闪电击 (Lightning Bolt)

**类型**: 瞬间

**费用**: {R}

**异 能**:

>{R}：对任意目标造成 3 点伤害。

---

### 规则分析

- **119.7**: 伤害立即结算，不需要等待
- **119.9**: 可以指定生物、玩家或鹏洛客为目标
- **702.19**: 闪电击没有闪现或敏捷

### 常见问题

**Q: 闪电击可以响应吗？**

> A: 可以。闪电击是瞬间，你可以在任意玩家回合的任意时间响应。

**Q: 闪电击的伤害可以被防止吗？**

> A: 可以，例如使用「防护」系列效应或「防止」效应。""",

            "先攻": """## 先攻 (First Strike)

**关键词能力** — 规则 702.7

### 效果

具有先攻的生物在**战斗伤害步骤**中分两段进行：

1. **先攻伤害步骤** — 只有具有先攻或双闪避的生物造成伤害
2. **普通伤害步骤** — 所有其他生物造成伤害

### 规则细节

- **702.7a**: 先攻属于静止式能力
- **702.7b**: 如果双方生物都具有先攻，同时在先攻伤害步骤造成伤害
- **702.7c**: 之后普通伤害步骤中，具有先攻的生物不再造成伤害

### 示例

| 攻击者 | 防御者 | 结果 |
|--------|--------|------|
| 鬼怪议事员 (先攻) | 人类士兵 | 鬼怪先造成 1 伤害击杀士兵，不受伤害 |
| 鬼怪议事员 | 人类士兵 (先攻) | 同时造成 1 伤害，双方阵亡 |""",

            "飞行": """## 飞行 (Flying)

**关键词能力** — 规则 702.9

### 效果

具有飞行的生物只能被具有飞行或践踏的生物阻挡。

### 阻挡规则

- **702.9a**: 飞行属于静止式能力
- **702.9b**: 没有飞行或践踏的生物不能阻挡具有飞行的生物

### 层级关系

| 能力 | 能否阻挡飞行生物 |
|------|------------------|
| 飞行 | ✓ |
| 践踏 | ✓ |
| 两者都没有 | ✗ |

### 常见误解

> Q: 具有飞行的生物可以被任何生物阻挡吗？

> A: 不可以。只有具有飞行或践踏的生物才能阻挡飞行生物。"""
        }

        # 关键词匹配
        for keyword, response in responses.items():
            if keyword in user_lower:
                return response.replace("{question}", user_message)

        return responses["default"].replace("{question}", user_message)

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

    def chat(self, user_message: str, session_id: str = "default", short_mode: bool = False, openid: str = None) -> Dict:
        """
        与 AI 裁判对话

        Args:
            user_message: 用户消息
            session_id: 会话ID，用于维护对话历史
            short_mode: 简短模式，减少 token 消耗（限制历史长度）
            openid: 微信 openid，用于 per-user agent 隔离

        Returns:
            {"success": bool, "reply": str}
        """
        import time
        logger = _get_ai_logger()

        # 请求限流检查
        rate_key = openid or session_id
        current_time = time.time()
        last_time = self._last_request_time.get(rate_key, 0)
        if current_time - last_time < self._rate_limit_seconds:
            return {
                "success": False,
                "reply": "异步处理中，请稍后刷新会话试试"
            }
        self._last_request_time[rate_key] = current_time

        # 获取 per-user agent（如果提供了 openid）
        agent_name = None
        if openid and self.agent_pool:
            try:
                agent_name, is_new = self.agent_pool.get_or_create_agent(openid)
                print(f"[chat] openid={openid}, agent={agent_name}, is_new={is_new}")
            except Exception as e:
                print(f"[chat] AgentPoolManager 错误: {e}")
                # 降级到默认 agent
                agent_name = None

        # 记录用户提问
        logger.info(f"=== 会话 [{session_id}] 用户提问 (short_mode={short_mode}, openid={openid}) ===\n{user_message}")

        # 自动检测并查询卡牌信息
        enhanced_message = self._enhance_message_with_cards(user_message)

        # 简短模式：使用简化版系统提示词
        if short_mode:
            system_prompt = self._get_short_system_prompt()
            max_history = 4  # 简短模式只保留最近2轮对话
        else:
            system_prompt = self.system_prompt
            max_history = 10  # 普通模式保留最近5轮对话（控制 token 消耗）

        # 获取或初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": system_prompt}
            ]
        else:
            # 更新系统提示词（以支持切换模式）
            if self.conversation_history[session_id][0]["role"] == "system":
                self.conversation_history[session_id][0]["content"] = system_prompt

        history = self.conversation_history[session_id]

        # 自动截断：只保留 system + 最近 max_history 条消息（控制 token 消耗）
        if len(history) > max_history + 1:
            history = [history[0]] + history[-(max_history):]

        # 添加用户消息（增强版）
        history.append({"role": "user", "content": enhanced_message})

        # 构建调试信息
        debug_info = {
            "session_id": session_id,
            "user_message": user_message,
            "enhanced_message": enhanced_message[:500] + "..." if len(enhanced_message) > 500 else enhanced_message,
            "message_count": len(history),
            "card_query_performed": enhanced_message != user_message,
            "agent_name": agent_name,
            "openid": openid
        }

        # 调用 API（优先使用 OpenCLAW Gateway）
        reply = None
        if self.openclaw_enabled:
            print("尝试调用 OpenCLAW Gateway...")
            reply = self._call_openclaw_gateway(history, agent_name=agent_name)
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

            # 使用统一日志服务记录
            log_info("ai_judge", f"会话 [{session_id}] 用户提问", {
                "message": user_message[:200],
                "session_id": session_id
            })
            log_info("ai_judge", f"会话 [{session_id}] AI 回复", {
                "reply_length": len(reply),
                "reply_preview": reply[:200]
            })

            # 限制历史长度（保留 system + 最近 max_history 条消息）
            if len(history) > max_history + 1:
                self.conversation_history[session_id] = [history[0]] + history[-(max_history):]

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

    def stream_chat(self, user_message: str, session_id: str = "default", short_mode: bool = False):
        """
        与 AI 裁判对话 - 流式版本
        返回生成器，逐步 yield 内容片段

        Args:
            user_message: 用户消息
            session_id: 会话ID，用于维护对话历史
            short_mode: 简短模式，减少 token 消耗

        Yields:
            {"content": str} - 内容片段
            {"done": bool} - 完成信号
            {"error": str} - 错误信息
        """
        logger = _get_ai_logger()

        # 记录用户提问
        logger.info(f"=== 会话 [{session_id}] 流式提问 (short_mode={short_mode}) ===\n{user_message}")

        if not self.api_key and not self.mock_mode:
            logger.error("AI 裁判 API Key 未配置")
            yield {"error": "AI 裁判服务暂未配置，请联系管理员。"}
            return

        # 自动检测并查询卡牌信息
        enhanced_message = self._enhance_message_with_cards(user_message)

        # 简短模式：使用简化版系统提示词
        if short_mode:
            system_prompt = self._get_short_system_prompt()
            max_history = 4  # 简短模式只保留最近2轮对话
        else:
            system_prompt = self.system_prompt
            max_history = 10  # 普通模式保留最近5轮对话（控制 token 消耗）

        # 获取或初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": system_prompt}
            ]
        else:
            # 更新系统提示词（以支持切换模式）
            if self.conversation_history[session_id][0]["role"] == "system":
                self.conversation_history[session_id][0]["content"] = system_prompt

        history = self.conversation_history[session_id]

        # 自动截断：只保留 system + 最近 max_history 条消息（控制 token 消耗）
        if len(history) > max_history + 1:
            history = [history[0]] + history[-(max_history):]

        # 添加用户消息（增强版）
        history.append({"role": "user", "content": enhanced_message})

        # 流式调用 API（优先使用 OpenCLAW）
        full_reply = ""

        if self.openclaw_enabled:
            print("流式请求：尝试调用 OpenCLAW Gateway...")
            # 调用 OpenCLAW Gateway（简化版，不支持流式，所以直接返回完整响应）
            reply = self._call_openclaw_gateway(history)
            if reply:
                # 模拟流式输出
                for i in range(0, len(reply), 10):
                    yield {"content": reply[i:i+10]}
                    import time
                    time.sleep(0.05)
                full_reply = reply
            else:
                yield {"error": "OpenCLAW 调用失败"}
                return
        else:
            # 使用 MiniMax 流式 API
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

        # 更新会话历史
        self.conversation_history[session_id] = history

        logger.info(f"=== 会话 [{session_id}] 流式回复完成 ===")
        yield {"done": True}

    def clear_session(self, session_id: str = "default", agent_name: str = None):
        """清除会话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

        # 同时删除 OpenCLAW 服务器上的 session 文件
        try:
            from backend.services.openclaw_client import OpenCLAWClient
            client = OpenCLAWClient()
            client.delete_session(agent_name=agent_name, session_id=session_id)
            client.close()
        except Exception as e:
            print(f"删除远程 session 文件失败: {e}")

    def new_session(self, session_id: str = "default", reset_agent: bool = True) -> Dict:
        """
        创建新会话

        清除当前会话的历史记录，并可选地重置 OpenCLAW Agent

        Args:
            session_id: 会话 ID
            reset_agent: 是否重置服务器端的 Agent 状态

        Returns:
            结果字典
        """
        # 清除本地会话历史
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

        result = {
            "success": True,
            "session_id": session_id,
            "message": "会话已创建",
            "agent_reset": False
        }

        # 如果需要重置服务器端 Agent
        if reset_agent and self.openclaw_enabled and not self.mock_mode:
            try:
                if OpenCLAWClient:
                    client = OpenCLAWClient(
                        host=self.openclaw_host,
                        port=self.openclaw_port,
                        username=self.openclaw_ssh_user,
                        password=self.openclaw_ssh_password,
                        key_content=self.openclaw_ssh_key_content,
                        agent=self.openclaw_agent
                    )

                    # 发送重置命令
                    reset_result = client.call_agent("/reset")
                    client.close()

                    if reset_result:
                        result["agent_reset"] = True
                        result["message"] = "会话已创建，Agent 已重置"
                else:
                    # 使用原有的 paramiko 实现
                    result = self._reset_agent_legacy(session_id, result)

            except Exception as e:
                print(f"重置 Agent 失败: {e}")
                result["message"] = f"会话已创建，但 Agent 重置失败: {e}"

        return result

    def _reset_agent_legacy(self, session_id: str, result: Dict) -> Dict:
        """重置 Agent - 原有实现"""
        import paramiko

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.openclaw_ssh_key_content:
                from io import BytesIO
                import base64
                key_file = BytesIO(base64.b64decode(self.openclaw_ssh_key_content))
                pkey = paramiko.Ed25519Key.from_private_key(key_file)
                client.connect(
                    self.openclaw_host,
                    username=self.openclaw_ssh_user,
                    pkey=pkey,
                    timeout=30
                )
            elif self.openclaw_ssh_key:
                client.connect(
                    self.openclaw_host,
                    username=self.openclaw_ssh_user,
                    key_filename=self.openclaw_ssh_key,
                    timeout=30
                )
            elif self.openclaw_ssh_password:
                client.connect(
                    self.openclaw_host,
                    username=self.openclaw_ssh_user,
                    password=self.openclaw_ssh_password,
                    timeout=30
                )
            else:
                return result

            # 发送重置命令
            cmd = f'bash -i -c "openclaw agent --agent {self.openclaw_agent} -m \\"/reset\\" --json"'
            stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
            output = stdout.read().decode()
            client.close()

            # 尝试解析响应
            try:
                json_result = json.loads(output)
                if json_result.get("status") == "ok":
                    result["agent_reset"] = True
                    result["message"] = "会话已创建，Agent 已重置"
            except:
                pass

        except Exception as e:
            print(f"重置 Agent 失败: {e}")

        return result


# 全局实例
ai_judge_service = AIJudgeService()
