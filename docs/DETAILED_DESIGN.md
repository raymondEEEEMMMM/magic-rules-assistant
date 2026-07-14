# mtgAsk 详细设计文档

## 1. API 端点规范

### 1.1 服务状态

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/` | GET | 服务状态检查，返回 `{"message": "...", "status": "ok"}` |

### 1.2 微信消息接收

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/wechat` | GET | 微信服务器验证（signature 签名校验） |
| `/wechat` | POST | 接收微信消息，响应 XML 格式 |

**微信消息 POST 请求体示例：**
```xml
<xml>
    <ToUserName><![CDATA[to_user]]></ToUserName>
    <FromUserName><![CDATA[from_user]]></FromUserName>
    <CreateTime>1234567890</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[content]]></Content>
</xml>
```

**事件消息 MsgType 为 `event`，Event 字段包括：**
- `subscribe`：用户关注公众号
- `unsubscribe`：用户取消关注

### 1.3 规则搜索 API

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/search` | GET | 综合规则搜索 |
| `/api/keyword` | GET | 关键词异能查询 |
| `/api/rule` | GET | 按规则编号查询规则 |

**搜索参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `q` | string | 是 | 搜索关键词 |
| `k` | string | 是 | 关键词异能名称（keyword API） |
| `n` | string | 是 | 规则编号，如 `702.9`、`101.1` |

**响应示例：**
```json
{
  "query": "飞行",
  "results": {
    "rules": [...],
    "keyword_abilities": [...],
    "cards": [...],
    "qa_templates": [...]
  }
}
```

### 1.4 卡牌查询 API

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/card` | GET | 卡牌搜索（MTGCH API） |
| `/api/mtgch/search` | GET | MTGCH 卡牌搜索 |
| `/api/mtgch/card` | GET | 单张卡牌详情 |
| `/api/mtgch/random` | GET | 随机卡牌 |
| `/api/mtgch/autocomplete` | GET | 自动补全 |
| `/api/mtgch/sets` | GET | 系列列表 |
| `/api/scryfall/set/{code}/cards` | GET | Scryfall 系列卡牌（含图片） |
| `/api/secret-lair/cards` | GET | Secret Lair 卡牌（按月分组） |
| `/api/secret-lair/search` | GET | Secret Lair 卡牌搜索 |
| `/api/promos` | GET | Promo 卡快讯 |

**MTGCH 搜索参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|--------|------|
| `q` | string | 是 | - | 搜索关键词 |
| `page` | int | 否 | 1 | 页码 |
| `page_size` | int | 否 | 5 | 每页数量，最大 100 |
| `priority_chinese` | bool | 否 | true | 优先中文版本 |
| `order` | string | 否 | released_at | 排序字段（released_at 原版优先） |

**MTGCH 卡牌详情参数（二选一）：**
| 参数 | 类型 | 说明 |
|-----|------|------|
| `id` | string | 卡牌 UUID |
| `set` + `number` | string | 系列代码 + 收集编号 |

**响应示例：**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "闪电风暴",
      "name_en": "Lightning Storm",
      "type_line": "瞬间",
      "oracle_text": "Lightning Storm deals X damage...",
      "mana_cost": "{1}{R}{R}",
      "colors": ["R"],
      "rarity": "uncommon"
    }
  ],
  "total": 100
}
```

### 1.5 AI 裁判 API

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/ai-judge/init` | POST | 预热 AI Agent |
| `/api/ai-judge/chat` | POST | AI 裁判对话 |
| `/api/ai-judge/analyze` | POST | 游戏局势分析 |
| `/api/ai-judge/clear` | POST | 清除会话历史 |
| `/api/ai-judge/history` | GET/POST | 获取会话历史 |

**Chat 请求体：**
```json
{
  "message": "闪电击和塔莫耶夫敏捷的伤害顺序？",
  "session_id": "default",
  "clear_history": false,
  "short_mode": false,
  "openid": "user_openid"
}
```

**Chat 响应：**
```json
{
  "success": true,
  "reply": "根据万智牌规则...",
  "usage": {
    "prompt_tokens": 1000,
    "completion_tokens": 200
  }
}
```

**历史记录参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `openid` | string | 是 | 用户 openid |
| `session_id` | string | 否 | 指定会话 ID |
| `limit` | int | 否 | 10 | 返回数量 |
| `offset` | int | 否 | 0 | 分页偏移 |

### 1.6 套牌管理 API

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/deck/list` | GET | 获取用户套牌列表 |
| `/api/deck/add` | POST | 添加套牌 |
| `/api/deck/{id}` | PUT | 更新套牌 |
| `/api/deck/{id}` | DELETE | 删除套牌 |
| `/api/deck/cmc` | POST | 计算 AVG CMC |
| `/api/deck/parse-url` | GET | 解析 MTGGoldfish/Moxfield URL |

**添加/更新套牌请求体：**
```json
{
  "openid": "user_openid",
  "name": "红黑快攻",
  "format": "标准",
  "commander": "",
  "cards": [{"name": "闪电击", "count": 4}, ...],
  "totalCards": 60,
  "avgCMC": "2.34"
}
```

**URL 解析响应：**
```json
{
  "success": true,
  "name": "Deck Name",
  "cards": [{"name": "Card", "count": 4}, ...],
  "format": "标准"
}
```

### 1.7 规则更新 API

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/rules/update` | POST | 更新规则（从 Wizards of Coast） |
| `/api/rules/status` | GET | 获取规则版本状态 |
| `/api/rules/parse` | GET | 解析规则文件 |
| `/api/rules/vectorization` | GET | 获取向量化数据 |

### 1.8 其他 API

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/feedback` | POST | 提交用户反馈 |
| `/api/token/list` | GET | 获取 Token 列表 |
| `/api/homepage/cards` | GET | 获取首页卡片配置 |
| `/api/homepage/cards/{card_key}/hidden` | POST | 设置卡片隐藏状态 |
| `/api/admin/cleanup-sessions` | POST | 清理所有过期会话 |
| `/api/admin/agent-pool/stats` | POST | 获取 Agent 池统计 |

### 1.9 微信 HTTP 访问路径

微信小程序通过 `wx.cloud.callFunction` 调用云函数时使用以下路径：

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/wechat/api/search` | GET | 规则搜索 |
| `/wechat/api/keyword` | GET | 关键词异能 |
| `/wechat/api/mtgch/search` | GET | 卡牌搜索 |
| `/wechat/api/mtgch/card` | GET | 卡牌详情 |
| `/wechat/api/ai-judge/chat` | POST | AI 对话 |
| `/wechat/api/ai-judge/clear` | POST | 清除会话 |
| `/wechat/api/ai-judge/history` | GET | 获取历史 |

---

## 2. 数据库设计

### 2.1 MySQL 连接配置

| 配置项 | 值 |
|-------|-----|
| 主机 | sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com |
| 端口 | 27987（外网） |
| 用户 | mtgask |
| 数据库 | magic-rules-assistant-0a1904c329 |
| 字符集 | utf8mb4 |

**注意**：云函数必须使用外网地址，无法访问内网 VPC。

### 2.2 核心表结构

#### 2.2.1 rules_v2（综合规则表）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| rule_number | VARCHAR(20) | 规则编号（如 702.9、101.1a） |
| rule_title_cn | VARCHAR(255) | 中文标题 |
| rule_title_en | VARCHAR(255) | 英文标题 |
| rule_content_cn | TEXT | 中文内容 |
| rule_content_en | TEXT | 英文内容 |
| category | VARCHAR(50) | 分类 |

#### 2.2.2 keyword_abilities_v2（关键词异能表）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| keyword_cn | VARCHAR(100) | 中文关键词 |
| keyword_en | VARCHAR(100) | 英文关键词 |
| description_cn | TEXT | 中文简要描述 |
| description_en | TEXT | 英文简要描述 |
| rule_ref_cn | TEXT | 中文完整规则引用 |
| rule_ref_en | TEXT | 英文完整规则引用 |

#### 2.2.3 ai_agent_pool（AI Agent 池）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| openid | VARCHAR(128) UNIQUE | 微信 openid |
| agent_name | VARCHAR(128) | OpenCLAW Agent 名称 |
| created_at | DATETIME | 创建时间 |
| last_used_at | DATETIME | 最后使用时间 |
| is_idle | BOOLEAN | 是否空闲（可回收） |
| idle_since | DATETIME | 开始空闲时间 |
| message_count | INT | 消息计数 |

**索引：**
- `idx_openid`：openid 唯一索引
- `idx_last_used`：最后使用时间索引
- `idx_is_idle`：空闲状态索引

#### 2.2.4 ai_judge_daily_stats（每日统计）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| openid | VARCHAR(128) | 微信 openid |
| date | DATE | 统计日期 |
| question_count | INT | 当日提问次数 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**唯一键：** `uk_openid_date (openid, date)`

#### 2.2.5 decks（套牌表）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| openid | VARCHAR(128) | 微信 openid |
| name | VARCHAR(255) | 套牌名称 |
| format | VARCHAR(64) | 赛制 |
| commander | VARCHAR(255) | 指挥官 |
| cards | TEXT | 卡牌列表（JSON） |
| total_cards | INT | 总张数 |
| avg_cmc | VARCHAR(10) | 平均 CMC |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**索引：**
- `idx_openid`：openid 索引
- `idx_created`：创建时间索引

#### 2.2.6 feedbacks（用户反馈表）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| openid | VARCHAR(128) | 微信 openid |
| content | TEXT | 反馈内容 |
| contact | VARCHAR(128) | 联系方式 |
| type | VARCHAR(20) | 反馈类型（suggestion/bug/other） |
| status | VARCHAR(20) | 状态（pending/resolved） |
| created_at | DATETIME | 创建时间 |

**索引：**
- `idx_openid`：openid 索引
- `idx_status`：状态索引

#### 2.2.7 homepage_card_config（首页卡片配置）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| card_key | VARCHAR(50) UNIQUE | 卡片标识 |
| card_name | VARCHAR(100) | 卡片名称 |
| hidden | BOOLEAN | 是否隐藏 |
| sort_order | INT | 排序顺序 |

**默认配置：**
| card_key | card_name | sort_order |
|----------|-----------|------------|
| ai_judge | AI 裁判 | 1 |
| token | Token 生成器 | 2 |
| promos | Promo 卡快讯 | 3 |
| counter | 生命值计数器 | 4 |
| dice | 骰子 & 随机 | 5 |
| deck | 我的套牌 | 6 |

---

## 3. 服务层设计

### 3.1 RuleService（规则服务）

**文件：** `services/rule_service.py`

```python
class RuleService:
    def __init__(self, db: RuleDatabase)
    
    def search_rules(self, query: str) -> Dict
    """综合搜索规则（规则 + 关键词异能 + 卡牌 + 问答模板）"""
    
    def get_keyword_ability(self, keyword: str) -> Optional[Dict]
    """获取关键词异能"""
    
    def get_card_rule(self, card_name: str) -> Optional[Dict]
    """获取卡牌规则（当前返回 None，卡牌通过 MTGCH API 查询）"""
    
    def format_response(self, search_results: Dict) -> str
    """格式化搜索结果为可读文本"""
```

**搜索流程：**
1. 从查询中提取关键词（分词 + 停用词过滤）
2. 搜索关键词异能（精确匹配）
3. 文本搜索规则（模糊匹配）
4. 搜索卡牌（当前未实现）
5. 搜索问答模板

### 3.2 MTGCHAPIClient（MTGCH API 客户端）

**文件：** `services/mtgch_api.py`

```python
class MTGCHAPIClient:
    BASE_URL = "https://mtgch.com/api/v1"
    
    def __init__(self, timeout: int = 10)
    
    def search_cards(self, query, page=1, page_size=20, 
                     priority_chinese=True, order=None, unique=None) -> Dict
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict]
    
    def get_card_by_set_and_number(self, set_code: str, 
                                   collector_number: str) -> Optional[Dict]
    
    def get_card_versions(self, card_id: str, limit=100) -> List[Dict]
    
    def get_random_card(self) -> Optional[Dict]
    
    def get_adjacent_card(self, set_code, collector_number, direction) -> Optional[Dict]
    
    def autocomplete(self, query, size=10, is_for_deck=False, page=1) -> Dict
    
    def get_sets(self) -> List[Dict]
    
    def get_set_by_code(self, set_code: str) -> Optional[Dict]
    
    def get_set_cards(self, set_code, order=None, unique=None,
                      priority_chinese=True, page=1, page_size=20) -> Dict
```

### 3.3 AIJudgeService（AI 裁判服务）

**文件：** `services/ai_judge_service.py`

```python
class AIJudgeService:
    RULE_FILES = [
        "markdown/glossarycn.md",
        "markdown/glossary.md",
        "references/triggered-abilities.md",
        "references/stack-priority.md",
        "references/continuous-effects.md",
        "references/copy-effects.md",
        "references/prevention-effects.md",
        "references/replacement-effects.md",
    ]
    
    def __init__(self)
    
    def chat(self, message: str, session_id: str = "default",
             short_mode: bool = False, openid: str = None) -> Dict
    """与 AI 裁判对话"""
    
    def analyze(self, game_state: Dict) -> Dict
    """分析游戏局势"""
    
    def clear_session(self, session_id: str, agent_name: str = None)
    """清除会话历史"""
    
    def init_agent(self, openid: str) -> Dict
    """预热/初始化 Agent"""
```

**每日限制：**
- 默认每日 10 次（可通过 `AI_JUDGE_DAILY_LIMIT` 配置）
- 限制通过 `ai_judge_daily_stats` 表实现
- 无 openid 的用户不受限制

**回复清理：**
- 过滤 OpenCLAW 返回的错误信息
- 移除敏感路径（`/root/`、`/var/`、`node_modules/` 等）

### 3.4 OpenCLAWClient（OpenCLAW SSH 客户端）

**文件：** `services/openclaw_client.py`

```python
class OpenCLAWClient:
    def __init__(self)
    
    def connect(self) -> bool
    """建立 SSH 连接"""
    
    def close(self)
    """关闭 SSH 连接"""
    
    def execute_command(self, command: str, timeout: int = 120) -> Dict
    """执行 openclaw 命令"""
    
    def chat(self, message: str, agent: str = None, 
             session_id: str = "default") -> Dict
    """通过 openclaw agent chat 执行对话"""
    
    def get_sessions(self, agent: str = None, limit: int = 10,
                     offset: int = 0) -> List[Dict]
    """获取会话列表"""
    
    def get_session_messages(self, agent: str, session_id: str,
                             limit: int = 10) -> List[Dict]
    """获取会话消息历史"""
```

### 3.5 AgentPoolManager（Agent 池管理器）

**文件：** `services/agent_pool_manager.py`

```python
class AgentPoolManager:
    def __init__(self)
    
    def get_or_create_agent(self, openid: str) -> str
    """获取或创建用户的 Agent"""
    
    def get_agent_by_openid(self, openid: str) -> Optional[Dict]
    """通过 openid 获取 Agent 信息"""
    
    def mark_agent_idle(self, openid: str) -> bool
    """标记 Agent 为空闲"""
    
    def cleanup_idle_agents(self) -> int
    """清理空闲超时的 Agents，返回清理数量"""
    
    def cleanup_all_sessions(self) -> Dict
    """清理所有 OpenCLAW 过期会话"""
    
    def get_pool_stats(self) -> Dict
    """获取 Agent 池统计信息"""
```

**Agent 命名：** `user_{sanitized_openid}`
**最大 Agent 数：** 100（通过 `OPENCLAW_MAX_AGENTS` 配置）
**空闲超时：** 30 分钟（通过 `OPENCLAW_IDLE_TIMEOUT` 配置）

### 3.6 Scheduler（定时任务调度器）

**文件：** `services/scheduler.py`

```python
class RuleScheduler:
    def start()
    """启动调度器"""
    
    def stop()
    """停止调度器"""
    
    def set_update_callback(self, callback: Callable)
    """设置更新回调函数"""
```

**定时任务：**
| 任务 | 触发时间 | 说明 |
|-----|---------|------|
| `rules_update` | 每天 03:00 | 检查规则更新 |
| `rules_full_check` | 每周一 10:00 | 全面检查规则 |

---

## 4. 微信消息处理

### 4.1 MessageHandler

**文件：** `backend/wechat/handlers.py`

```python
class MessageHandler:
    def __init__(self, rule_service: RuleService)
    
    def handle_text_message(self, user_message: str) -> str
    """处理文本消息，返回回复文本"""
    
    def handle_event(self, event_type: str) -> Optional[str]
    """处理事件消息"""
```

### 4.2 消息路由规则

| 消息格式 | 处理逻辑 | 示例 |
|---------|---------|------|
| `卡牌:名称` | MTGCH API 查询 | `卡牌:黑莲花` |
| `card:名称` | MTGCH API 查询 | `card:Black Lotus` |
| `异能:关键词` | 关键词异能查询 | `异能:飞行` |
| `ability:关键词` | 关键词异能查询 | `ability:Flying` |
| `裁判:问题` | AI 裁判对话 | `裁判:闪电击伤害顺序` |
| `judge:问题` | AI 裁判对话 | `judge:stack priority` |
| `/help` | 帮助信息 | - |
| `/start` | 欢迎信息 | - |
| 其他文本 | 规则综合搜索 | `先攻是什么` |

### 4.3 响应格式

文本消息响应为微信 XML 格式：
```xml
<xml>
    <ToUserName><![CDATA[to_user]]></ToUserName>
    <FromUserName><![CDATA[from_user]]></FromUserName>
    <CreateTime>1234567890</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[回复内容]]></Content>
</xml>
```

---

## 5. 配置管理

### 5.1 配置类（Config）

**文件：** `backend/config.py`

```python
class Config:
    # 微信公众号配置
    WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
    WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")
    WECHAT_ENCODING_AES_KEY = os.getenv("WECHAT_ENCODING_AES_KEY", "")

    # MiniMax配置
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

    # OpenCLAW Gateway 配置
    OPENCLAW_ENABLED = os.getenv("OPENCLAW_ENABLED", "true").lower() == "true"
    OPENCLAW_HOST = os.getenv("OPENCLAW_HOST", "")
    OPENCLAW_PORT = os.getenv("OPENCLAW_PORT", "19601")
    OPENCLAW_SSH_USER = os.getenv("OPENCLAW_SSH_USER", "openclaw")
    OPENCLAW_SSH_PASSWORD = os.getenv("OPENCLAW_SSH_PASSWORD", "")
    OPENCLAW_SSH_KEY = os.getenv("OPENCLAW_SSH_KEY", "")
    OPENCLAW_SSH_KEY_CONTENT = os.getenv("OPENCLAW_SSH_KEY_CONTENT", "")
    OPENCLAW_AGENT = os.getenv("OPENCLAW_AGENT", "main")

    # Agent 池配置
    OPENCLAW_MAX_AGENTS = int(os.getenv("OPENCLAW_MAX_AGENTS", "100"))
    OPENCLAW_IDLE_TIMEOUT = int(os.getenv("OPENCLAW_IDLE_TIMEOUT", "30"))

    # Mock 模式配置
    OPENCLAW_MOCK = os.getenv("OPENCLAW_MOCK", "false").lower() == "true"

    # AI Judge 每日限制
    AI_JUDGE_DAILY_LIMIT = int(os.getenv("AI_JUDGE_DAILY_LIMIT", "10"))

    # 数据库配置
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/magic_rules.db")

    # API配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # 日志配置
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    LOG_FILE = os.getenv("LOG_FILE", f"mtgask_{datetime.now().strftime('%Y%m%d')}.log")
```

### 5.2 环境变量说明

| 变量 | 说明 | 必填 |
|-----|------|-----|
| `WECHAT_TOKEN` | 微信验证 Token | 是 |
| `MINIMAX_API_KEY` | MiniMax API 密钥 | AI 裁判必填 |
| `OPENCLAW_HOST` | OpenCLAW 服务器 IP | OpenCLAW 必填 |
| `OPENCLAW_SSH_KEY_CONTENT` | SSH 私钥内容（Base64） | OpenCLAW 必填 |
| `MYSQL_HOST` | MySQL 主机 | 云函数必填 |
| `MYSQL_PORT` | MySQL 端口 | 否（默认 27987） |
| `MYSQL_USER` | MySQL 用户 | 云函数必填 |
| `MYSQL_PASSWORD` | MySQL 密码 | 云函数必填 |
| `MYSQL_DATABASE` | 数据库名 | 否 |
| `TCB_ENV_ID` | CloudBase 环境 ID | 否 |

---

## 6. AI 裁判知识库结构

**本地路径：** `functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/`

```
magic-comp-rules-zh-cn-agent/
├── skill.md                      # 技能定义
├── cc.pem                        # SSH 客户端证书
├── markdown/                     # 规则文件
│   ├── 1.md ~ 9.md             # 万智牌规则 1-9 章（中文）
│   ├── glossarycn.md            # 中文术语表
│   ├── glossary.md              # 英文术语表
│   ├── index.md                # 规则索引
│   ├── intro.md                # 简介
│   ├── credits.md              # 贡献者
│   └── translatedterms.md
├── references/                   # 参考文档
│   ├── triggered-abilities.md  # 触发式异能
│   ├── stack-priority.md        # 堆叠与优先权
│   ├── continuous-effects.md     # 持续效应
│   ├── copy-effects.md          # 复制效应
│   ├── prevention-effects.md    # 防止效应
│   └── replacement-effects.md   # 替代式效应
└── scripts/
    └── sync_judge_knowledge.py  # 同步脚本
```

---

*文档版本: 1.0*
*最后更新: 2026-05-27*