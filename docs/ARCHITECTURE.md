# mtgAsk 项目架构文档

## 1. 系统概述

mtgAsk 是一个基于微信生态的万智牌（Magic: The Gathering）规则智能问答系统，为牌手提供便捷的规则查询、卡牌信息和关键词异能检索服务。

### 1.1 核心能力

- **规则查询**：基于万智牌官方综合规则的综合搜索
- **卡牌查询**：通过卡牌名称查询规则文本
- **关键词检索**：搜索关键词异能的详细解释
- **定时更新**：自动同步官方规则更新
- **微信集成**：通过微信公众号提供交互式问答

### 1.2 技术架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              客户端层                                     │
│  ┌─────────────────┐                   ┌─────────────────────────────┐ │
│  │   微信小程序     │                   │      微信公众号              │ │
│  │  (miniprogram) │                   │      (WeChat MP)            │ │
│  └────────┬────────┘                   └──────────────┬──────────────┘ │
│           │                                           │                  │
│           │  HTTPS API                                │  微信消息       │
│           │                                            │                  │
└───────────┼───────────────────────────────────────────┼─────────────────┘
            │                                            │
            ▼                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           云服务层 (CloudBase)                            │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │                        云函数 (mtgAsk)                                 ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐││
│  │  │  路由层      │  │  业务逻辑层   │  │  数据访问层  │  │  微信处理   │││
│  │  │ (FastAPI)   │──│ (Services)  │──│ (Database)  │  │ (Handlers)  │││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                     │                                       │
│                                     ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │                        MySQL 数据库                                    ││
│  │  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌────────────────────┐ ││
│  │  │  rules   │ │keyword_abilities│ │card_rules │ │    qa_templates   │ ││
│  │  └──────────┘ └──────────────┘ └────────────┘ └────────────────────┘ ││
│  └───────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           外部数据源                                       │
│  ┌─────────────────────┐    ┌─────────────────────┐                     │
│  │   MTGJSON           │    │   Wizards of Coast  │                     │
│  │   (卡牌数据)         │    │   (官方规则)         │                     │
│  └─────────────────────┘    └─────────────────────┘                     │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 系统架构

### 2.1 整体架构

系统采用 **三层架构** 设计：

1. **接入层**：微信小程序 + 微信公众号
2. **服务层**：云函数（CloudBase Functions）
3. **数据层**：MySQL 数据库 + 外部数据源

### 2.2 部署架构

| 组件 | 部署平台 | 说明 |
|-----|---------|------|
| 云函数 | 腾讯云 CloudBase | Python 3.10 运行时 |
| 数据库 | 腾讯云 MySQL | 主数据库 |
| 小程序 | 微信小程序平台 | 前端应用 |
| 公众号 | 微信公众平台 | 消息交互 |

---

## 3. 模块设计

### 3.1 后端模块结构

```
functions/mtgAsk/
├── backend/
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库访问层
│   ├── routes.py         # API 路由定义
│   ├── main.py           # 服务入口
│   │
│   ├── services/          # 业务逻辑层
│   │   ├── rule_service.py       # 规则查询服务
│   │   ├── card_service.py       # 卡牌查询服务
│   │   ├── rule_downloader.py    # 规则下载服务
│   │   ├── card_downloader.py   # 卡牌下载服务
│   │   ├── scheduler.py          # 定时任务调度
│   │   └── mtgch_api.py          # MTGCH API 集成
│   │
│   └── wechat/           # 微信处理模块
│       └── handlers.py   # 消息处理器
│
├── data/                  # 本地数据目录
│   └── magic_rules.db   # SQLite 本地缓存（开发用）
│
└── index.py             # 云函数入口
```

### 3.2 前端模块结构

```
miniprogram/
├── app.js               # 小程序入口
├── app.json             # 全局配置
│
├── pages/               # 页面目录
│   ├── index/           # 首页
│   ├── search/          # 搜索页
│   ├── card/            # 卡牌详情页
│   ├── rule/            # 规则详情页
│   ├── keyword/         # 关键词页
│   ├── apitest/         # API 测试页
│   ├── test/            # 测试页
│   └── example/         # 示例页
│
├── components/          # 组件目录
├── utils/               # 工具函数
└── images/             # 图片资源
```

---

## 4. 核心模块说明

### 4.1 路由层 (routes.py)

基于 FastAPI 框架构建，提供 RESTful API 接口。

**核心端点：**

| 路径 | 方法 | 功能 |
|-----|------|------|
| `/` | GET | 服务状态检查 |
| `/wechat` | GET | 微信服务器验证 |
| `/wechat` | POST | 接收微信消息 |
| `/api/search` | GET | 规则综合搜索 |
| `/api/keyword` | GET | 关键词查询 |
| `/api/card` | GET | 卡牌查询 |
| `/api/rules/update` | POST | 更新规则 |
| `/api/rules/status` | GET | 规则状态 |

### 4.2 业务逻辑层 (services/)

#### RuleService
- 规则全文搜索
- 关键词异能查询
- 卡牌规则查询
- 结果格式化

#### RuleDownloader
- 从 Wizards of Coast 下载最新规则
- 规则版本检测
- 规则解析入库

#### CardDownloader
- 从 MTGJSON 下载卡牌数据
- 卡牌信息同步

#### Scheduler
- 定时任务调度
- 每天 03:00 检查规则更新
- 每周一 10:00 执行完整同步

### 4.3 数据访问层 (database.py)

支持两种数据库：
- **云端**：MySQL (CloudBase)
- **本地**：SQLite (开发调试)

自动检测运行环境并选择合适的数据库连接。

### 4.4 微信消息处理 (wechat/handlers.py)

消息类型处理：
- **文本消息**：规则搜索、卡牌查询、关键词查询
- **事件消息**：关注/取关处理

命令支持：
- `/help` - 帮助信息
- `/start` - 欢迎消息

快捷查询：
- `卡牌:{名称}` - 卡牌查询
- `异能:{关键词}` - 关键词查询

---

## 5. 数据模型

### 5.1 数据库表结构

| 表名 | 说明 |
|-----|------|
| `rules` | 综合规则表 |
| `keyword_abilities` | 关键词异能表 |
| `card_rules` | 卡牌规则表 |
| `qa_templates` | 问答模板表 |

### 5.2 关键词异能表 (keyword_abilities)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| keyword_name | VARCHAR | 关键词名称 |
| keyword_code | VARCHAR | 关键词代码 (如 702.9) |
| description | TEXT | 简要描述 |
| full_text | TEXT | 完整规则文本 |
| examples | TEXT | 示例 (JSON 数组) |

### 5.3 卡牌规则表 (card_rules)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| card_name | VARCHAR | 卡牌名称 |
| card_type | VARCHAR | 卡牌类型 |
| oracle_text | TEXT | 规则文本 |
| related_rules | TEXT | 相关规则 (JSON 数组) |

---

## 6. 部署架构

### 6.1 云函数部署

```json
{
  "name": "mtgAsk",
  "runtime": "Python3.10",
  "handler": "index.main_handler",
  "timeout": 60,
  "memorySize": 512
}
```

### 6.2 环境配置

| 变量 | 说明 | 示例值 |
|-----|------|-------|
| ENVIRONMENT | 运行环境 | production |
| WECHAT_TOKEN | 微信验证 Token | wx_mtg_rules_2024 |
| MYSQL_HOST | MySQL 主机 | sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com |
| MYSQL_PORT | MySQL 端口 | 27987 |
| MYSQL_USER | MySQL 用户 | mtgask |
| MYSQL_DATABASE | 数据库名称 | magic-rules-assistant-0a1904c329 |
| OPENCLAW_ENABLED | 启用 OpenCLAW | true |
| OPENCLAW_HOST | OpenCLAW 服务器 IP | (环境变量) |
| OPENCLAW_PORT | OpenCLAW 端口 | 19601 |
| OPENCLAW_SSH_USER | SSH 用户名 | openclaw |
| OPENCLAW_SSH_KEY | SSH 密钥 | (环境变量) |
| OPENCLAW_SSH_KEY_CONTENT | SSH 私钥内容 | (环境变量) |
| OPENCLAW_AGENT | Agent 名称 | main |

### 6.3 访问地址

- **云函数 API**: `https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com`
- **小程序**: 微信小程序平台

---

## 7. AI 裁判系统架构

### 7.1 系统概述

AI 裁判系统基于 OpenCLAW Gateway 实现，提供智能万智牌规则问答服务。

### 7.2 部署架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           mtgAsk 系统                                       │
│  ┌─────────────────┐         ┌─────────────────┐                          │
│  │   微信小程序     │         │   微信公众号     │                          │
│  └────────┬────────┘         └────────┬────────┘                          │
│           │                            │                                   │
│           │    HTTPS API               │  微信消息                          │
│           ▼                            ▼                                   │
│  ┌─────────────────────────────────────────────┐                          │
│  │            云函数 mtgAsk                     │                          │
│  │  ┌─────────────────────────────────────┐    │                          │
│  │  │      ai_judge_service.py           │    │                          │
│  │  │   /api/ai-judge/chat (POST)        │    │                          │
│  │  │   /api/ai-judge/analyze (POST)     │────┼──SSH+CLI──▶            │
│  │  └─────────────────────────────────────┘    │                          │
│  └─────────────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      自建服务器 (OpenCLAW Gateway)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  openclaw agent CLI                                                 │  │
│  │  ├── Skill: mtg-judge                                              │  │
│  │  ├── 知识库: workspace/skills/ai_judge/                           │  │
│  │  │   ├── markdown/ (规则 1-9 章 + 术语表)                          │  │
│  │  │   └── knowledge-map/ (知识图谱)                                │  │
│  │  └── LLM: MiniMax API                                              │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 组件说明

| 组件 | 部署位置 | 说明 |
|-----|---------|------|
| mtgAsk 云函数 | CloudBase | Python 云函数，处理微信消息和 API 请求 |
| ai_judge_service | CloudBase | AI 裁判业务逻辑，通过 SSH 调用 Gateway |
| OpenCLAW Gateway | 自建服务器 | Docker 部署的 AI Agent 服务 |
| MiniMax API | 云厂商 | LLM 提供商 |
| 知识库 | 自建服务器 | 万智牌规则、术语、知识图谱 |

### 7.4 部署配置

**自建服务器配置：**

| 属性 | 值 |
|------|-----|
| 服务器 IP | (环境变量) |
| SSH 端口 | 22 |
| SSH 用户 | openclaw |
| Agent 名称 | main |
| Docker 端口 | 18789 |

**云函数环境变量：**

| 变量 | 说明 | 默认值 |
|-----|------|-------|
| OPENCLAW_ENABLED | 启用 OpenCLAW | true |
| OPENCLAW_HOST | 服务器 IP | (环境变量) |
| OPENCLAW_PORT | SSH 端口 | 22 |
| OPENCLAW_SSH_USER | SSH 用户名 | openclaw |
| OPENCLAW_SSH_KEY | SSH 密钥路径 | (环境变量) |
| OPENCLAW_SSH_KEY_CONTENT | SSH 私钥内容 | (环境变量) |
| OPENCLAW_AGENT | Agent 名称 | main |
| OPENCLAW_MOCK | Mock 测试模式 | false |

### 7.5 知识库同步

**知识库来源：** GitHub (Kuuusoda/magic-comp-rules-zh-cn-agent)

**同步流程：**

```
GitHub ──同步脚本──▶ 本地目录 ──同步脚本──▶ 自建服务器
                 functions/mtgAsk/     workspace/skills/
                 backend/data/knowledge ai_judge/
```

**同步文件列表：**

| 类别 | 文件 |
|-----|------|
| 规则 | markdown/1.md ~ 9.md |
| 术语 | markdown/glossarycn.md, translatedterms.md |
| 知识图谱 | knowledge-map/*.md |

**同步脚本位置：** `functions/mtgAsk/scripts/sync_judge_knowledge.py`

**使用方式：**
```bash
# 同步所有
python functions/mtgAsk/scripts/sync_judge_knowledge.py

# 仅同步规则
python functions/mtgAsk/scripts/sync_judge_knowledge.py --rules

# 强制同步
python functions/mtgAsk/scripts/sync_judge_knowledge.py --force
```

### 7.6 API 端点

| 端点 | 方法 | 功能 |
|-----|------|------|
| `/api/ai-judge/chat` | POST | AI 裁判问答 |
| `/api/ai-judge/analyze` | POST | 游戏局势分析 |
| `/api/ai-judge/clear` | POST | 清除会话 |
| `/api/ai-judge/status` | GET | 服务状态 |

### 7.7 目录结构

**AI 裁判知识库目录（与 magic-comp-rules-zh-cn-agent 对齐）：**

```
functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/
├── skill.md              # 技能定义
├── 345.md                # 裁判技能定义（旧版兼容）
├── cc.pem                # SSH 客户端证书
├── markdown/             # 规则文件（1-9章 + 术语表）
│   ├── 1.md ~ 9.md
│   ├── glossarycn.md    # 中文术语表
│   ├── glossary.md       # 英文术语表
│   ├── index.md          # 规则索引
│   ├── intro.md          # 简介
│   ├── credits.md        # 贡献者
│   └── translatedterms.md
├── references/           # 知识图谱
│   ├── triggered-abilities.md
│   ├── stack-priority.md
│   ├── continuous-effects.md
│   ├── copy-effects.md
│   ├── prevention-effects.md
│   └── replacement-effects.md
└── scripts/
    └── sync_judge_knowledge.py # 同步脚本
```

**服务器端目录：**
```
/root/openclaw/workspace/skills/ai_judge/
└── (与本地目录结构相同)
```

---

## 8. 扩展性设计

### 8.1 缓存机制

- 热门查询结果缓存
- 规则版本缓存
- 向量化数据预加载

### 8.2 日志系统

- 请求日志
- 错误追踪
- 性能监控

---

## 9. 安全考虑

1. **微信签名验证**：所有微信请求经过 SHA1 签名验证
2. **环境变量隔离**：敏感信息通过环境变量管理
3. **数据库权限**：最小权限原则，区分读写权限
4. **API 限流**：防止恶意请求

---

## 10. 依赖技术栈

| 层级 | 技术 | 版本 |
|-----|------|------|
| 后端框架 | FastAPI | - |
| 数据库 | MySQL / SQLite | 5.7+ / 3.x |
| HTTP 客户端 | requests | - |
| 定时任务 | schedule | - |
| 前端框架 | 微信小程序原生 | - |
| 部署平台 | 腾讯云 CloudBase | - |

---

## 11. 目录结构总览

```
cbworkplace/
├── functions/mtgAsk/           # 云函数后端
│   ├── backend/
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库层
│   │   ├── routes.py           # 路由定义
│   │   ├── services/           # 业务服务
│   │   └── wechat/             # 微信处理
│   └── index.py                # 函数入口
│
├── miniprogram/                # 微信小程序
│   ├── pages/                  # 页面
│   ├── utils/                  # 工具
│   └── images/                 # 资源
│
├── deployment/                 # 部署配置
├── tests/                      # 测试代码
├── cloudbaserc.json            # 云函数配置
└── deploy.sh                   # 部署脚本
```

---

*文档版本: 1.0*
*最后更新: 2024*
