# AI Agent 架构文档

## 概述

AI 裁判功能基于 OpenCLAW Gateway 实现，支持 per-user agent 隔离，每个微信用户拥有独立的 AI agent。

## 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        小程序前端 (agent.js)                         │
│  - onLoad: aiJudgeInit(openid)  预热 Agent                         │
│  - 发送消息: aiJudgeChat(message, sessionId, openid)               │
│  - 刷新: aiJudgeHistory(openid, sessionId)                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CloudBase 云函数 (mtgAsk)                         │
│                                                                      │
│  routes.py                                                           │
│  ├── /api/ai-judge/init     ← 预热 Agent (新建/获取)                │
│  ├── /api/ai-judge/chat     ← 发送消息                              │
│  ├── /api/ai-judge/clear    ← 清除会话                              │
│  └── /api/ai-judge/history  ← 获取历史                              │
│                                                                      │
│  ai_judge_service.py                                                 │
│  └── AIJudgeService                                                  │
│       ├── init_agent(openid)       预热/获取 Agent                   │
│       ├── chat(message, ...)       发送消息                          │
│       └── clear_session(...)       清除会话                          │
│                                                                      │
│  agent_pool_manager.py                                               │
│  └── AgentPoolManager                                                │
│       ├── get_or_create_agent(openid)  获取或创建 Agent              │
│       ├── release_agent(openid)       标记为空闲                     │
│       └── cleanup_idle_agents()       清理空闲 Agent                 │
│                                                                      │
│  openclaw_client.py                                                  │
│  └── OpenCLAWClient (SSH 连接 Gateway)                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │  SSH (port 22)
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│               OpenCLAW Gateway (101.43.48.45)                        │
│                                                                      │
│  Host 文件系统 (systemd 管理)                                         │
│  ├── /home/openclaw/agents/{agent_name}/                            │
│  │    ├── SOUL.md              角色定义 prompt                       │
│  │    ├── IDENTITY.md          Agent 身份                            │
│  │    └── skills/ → /home/openclaw/.openclaw/workspace/skills       │
│  │                                                                      │
│  └── /home/openclaw/.openclaw/workspace/skills/ai_judge/            │
│       ├── SKILL.md              AI 裁判技能定义                      │
│       └── references/           裁判知识库                           │
│            ├── glossarycn.md    中文词汇表                           │
│            ├── glossary.md      英文词汇表                           │
│            └── ...                                                  │
│                                                                      │
│  Docker Sandbox (按需创建)                                           │
│  └── openclaw-sbx-agent-{agent_name}-main-*                         │
│       └── 挂载 workspace 目录                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. AgentPoolManager

**职责**：管理 Agent 的生命周期

**关键方法**：
- `get_or_create_agent(openid)` - 获取或创建用户的 Agent
- `release_agent(openid)` - 标记 Agent 为空闲
- `cleanup_idle_agents()` - 清理空闲超时的 Agent

**配置参数**：
- `MAX_AGENTS = 100` - 最大 Agent 数量
- `IDLE_TIMEOUT_MINUTES = 30` - 空闲超时时间（分钟）
- `RECYCLE_THRESHOLD = 80%` - 触发回收的容量阈值

**Agent 命名规则**：`user_{sanitized_openid}`
- 特殊字符处理：`@` → `_at_`，`-` → `_`，`.` → `_`

### 2. OpenCLAWClient

**职责**：通过 SSH 连接到 Gateway 执行命令

**连接方式**：
- SSH 密钥认证（Ed25519）
- Key 文件路径：`/tmp/openclaw_ssh_key`

**主要操作**：
- 创建 workspace 目录
- 创建 skills 软链接
- 注入 MTG prompt 到 SOUL.md
- 注册/删除 Agent

### 3. AIJudgeService

**职责**：处理 AI 裁判业务逻辑

**关键方法**：
- `init_agent(openid)` - 预热 Agent
- `chat(message, session_id, short_mode, openid)` - 发送消息
- `clear_session(session_id, agent_name)` - 清除会话

**安全措施**：
- 60 秒请求限流（防止刷接口）
- 回复内容过滤（`_sanitize_reply` 防止暴露服务器路径）

## API 接口

### POST /api/ai-judge/init

**用途**：预热 Agent，提前完成创建/获取

**参数**：
```json
{
  "openid": "user_xxx"
}
```

**返回**：
```json
{
  "success": true,
  "agent_name": "user_xxx",
  "is_new": true
}
```

**调用时机**：小程序 `onLoad` 时并行调用

### POST /api/ai-judge/chat

**用途**：发送消息给 AI 裁判

**参数**：
```json
{
  "message": "行旅在指挥官赛制中如何运作？",
  "session_id": "miniprogram_xxx",
  "openid": "user_xxx",
  "short_mode": false
}
```

**返回**：
```json
{
  "success": true,
  "reply": "关于行旅（Companion）..."
}
```

### POST /api/ai-judge/clear

**用途**：清除会话历史

**参数**：
```json
{
  "session_id": "miniprogram_xxx",
  "openid": "user_xxx"
}
```

### GET /api/ai-judge/history

**用途**：获取会话历史

**参数**：
```
openid=user_xxx
session_id=miniprogram_xxx (可选)
```

## Agent 生命周期

### 1. 创建阶段

```
用户首次访问
    │
    ▼
get_or_create_agent(openid)
    │
    ├─ 检查数据库是否有记录
    │     │
    │     ├─ 有 → 返回现有 agent_name，更新 last_used
    │     │
    │     └─ 无 → 继续创建
    │
    ▼
检查 Agent 数量是否达到上限
    │
    ├─ 是 → 执行回收/强制回收最老的
    │
    ▼
创建新 Agent
    │
    ├─ 1. SSH 到 Gateway
    ├─ 2. 创建 workspace 目录
    ├─ 3. 创建 skills 软链接
    ├─ 4. 注入 SOUL.md / IDENTITY.md
    ├─ 5. 注册 Agent (openclaw agents add)
    │
    ▼
保存到数据库
    │
    ▼
返回 agent_name, is_new=true
```

### 2. 使用阶段

```
用户发送消息
    │
    ▼
chat() → _call_openclaw_gateway()
    │
    ├─ 1. SSH 到 Gateway
    ├─ 2. 执行 openclaw agents chat 命令
    ├─ 3. Gateway 创建/复用 sandbox 容器
    ├─ 4. Agent 读取 skills/ai_judge/SKILL.md
    ├─ 5. Agent 调用 LLM (MiniMax API)
    ├─ 6. 返回回复
    │
    ▼
_sanitize_reply() 过滤敏感信息
    │
    ▼
返回给用户
```

### 3. 回收阶段

```
定时任务或容量不足
    │
    ▼
cleanup_idle_agents()
    │
    ├─ 1. 查询空闲超时的 Agent
    ├─ 2. SSH 到 Gateway
    ├─ 3. 删除 Agent (openclaw agents delete)
    ├─ 4. 清理 Docker 容器
    ├─ 5. 删除 workspace 目录
    │
    ▼
删除数据库记录
```

## 冷启动优化

**问题**：首次发送消息时，Agent 可能需要创建/初始化，导致等待时间长

**解决方案**：预热机制

```
小程序 onLoad
    │
    ├─ api.aiJudgeInit(openid)  ← 预热（不等待）
    └─ api.aiJudgeHistory(openid)  ← 获取历史
```

**效果**：
- 页面加载时，后台预热 Agent
- 用户发送消息时，Agent 已就绪
- 减少感知延迟

## 错误处理

### Skill 读取失败

**问题**：OpenCLAW 尝试从 pnpm 全局路径读取 skill 失败

**原因**：Sandbox 容器冷启动时序问题

**处理**：`_sanitize_reply()` 过滤错误信息，返回友好提示

```
回复包含 "Read: ... failed" → "抱歉，AI 裁判暂时无法回答此问题，请稍后再试。"
```

### 请求限流

**配置**：同一用户 60 秒内只能请求一次

**触发**：`rate_limit_seconds = 60`

**返回**：`"异步处理中，请稍后刷新会话试试"`

## 目录结构

```
Gateway (101.43.48.45):
/home/openclaw/
├── agents/                          # Agent workspace 根目录
│   └── user_{openid}/
│       ├── SOUL.md                  # 角色定义
│       ├── IDENTITY.md              # 身份信息
│       └── skills/ → ...            # skills 软链接
│
├── .openclaw/workspace/skills/       # 共享 skills
│   └── ai_judge/
│       ├── SKILL.md                 # 技能定义
│       └── references/              # 裁判知识库
│           ├── glossarycn.md
│           ├── glossary.md
│           └── ...
│
└── .openclaw/agents/                # Agent 注册配置
    └── openclaw.json

云函数 (CloudBase):
/Users/lianghaoming/cbworkplace/functions/mtgAsk/
├── backend/
│   ├── services/
│   │   ├── ai_judge_service.py      # AI 裁判服务
│   │   ├── agent_pool_manager.py    # Agent 池管理
│   │   └── openclaw_client.py       # SSH 客户端
│   └── routes.py                    # API 路由
└── index.py                         # 入口
```

## 相关文件

| 文件 | 作用 |
|------|------|
| `agent_pool_manager.py` | Agent 生命周期管理 |
| `openclaw_client.py` | SSH 连接 Gateway |
| `ai_judge_service.py` | 业务逻辑、限流、错误过滤 |
| `routes.py` | API 接口定义 |
| `agent.js` (小程序) | 前端调用 |
| `api.js` (小程序) | API 封装 |
