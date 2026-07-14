# mtgAsk 项目架构概述

## 1. 项目简介

mtgAsk 是一个基于微信生态的万智牌（Magic: The Gathering）规则智能问答系统，为牌手提供便捷的规则查询、卡牌检索和 AI 裁判对局分析服务。

### 1.1 核心功能

| 功能 | 说明 |
|-----|------|
| 规则查询 | 基于万智牌官方综合规则的综合搜索 |
| 卡牌查询 | 通过 MTGCH API 查询卡牌信息，原版优先 |
| 关键词异能 | 搜索关键词异能的详细解释 |
| AI 裁判 | 基于 OpenCLAW Gateway 的智能规则问答 |
| 定时更新 | 自动同步官方规则更新（每日 03:00 / 每周一 10:00） |
| 套牌管理 | 套牌列表、解析 URL、计算 AVG CMC |

### 1.2 技术栈

| 层级 | 技术 | 说明 |
|-----|------|-------|
| 前端 | 微信小程序 | miniprogram/ |
| 后端框架 | FastAPI | Python 3.10 云函数 |
| 数据库 | MySQL (CloudBase) | 云端主数据库 |
| AI 引擎 | OpenCLAW Gateway | 自建服务器，Docker 部署 |
| LLM | MiniMax API | AI 裁判对话 |
| 卡牌数据 | MTGCH API + Scryfall API | 卡牌查询 |
| 部署平台 | 腾讯云 CloudBase | 云函数 + MySQL |

---

## 2. 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              客户端层                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                          微信小程序 (miniprogram)                          │ │
│  │  - 卡牌搜索 / AI 对话 / 套牌管理 / Token 生成器 / Promo 卡快讯            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│             │                                                                │
│             │ HTTPS API                                                      │
│             ▼                                                                │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          云服务层 (CloudBase)                                     │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                          云函数 mtgAsk                                       ││
│  │  ┌────────────────────────────────────────────────────────────────────────┐   ││
│  │  │  路由层 (FastAPI)                                                     │   ││
│  │  │  /api/search, /api/keyword, /api/card, /api/ai-judge/chat, /api/deck/* │   ││
│  │  └────────────────────────────────────────────────────────────────────────┘   ││
│  │                                    │                                          ││
│  │  ┌─────────────────────────────────┼────────────────────────────────────┐  ││
│  │  │                                 ▼                                        │  ││
│  │  │  业务逻辑层 (Services)                                                 │  ││
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │  ││
│  │  │  │rule_service │ │mtgch_api     │ │ai_judge_svc │ │deck_service  │  │  ││
│  │  │  │ - 规则搜索    │ │ - 卡牌查询   │ │ - AI 对话    │ │ - 套牌管理   │  │  ││
│  │  │  │ - 关键词异能 │ │ - 自动补全   │ │ - SSH 调用   │ │ - URL 解析   │  │  ││
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘  │  ││
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │  ││
│  │  │  │scheduler     │ │openclaw_cli  │ │agent_pool_mgr│                    │  ││
│  │  │  │ - 定时任务    │ │ - SSH 客户端 │ │ - Agent 池   │                    │  ││
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘                    │  ││
│  │  └─────────────────────────────────────────────────────────────────────────┘  ││
│  │                                    │                                        ││
│  │  ┌─────────────────────────────────┼────────────────────────────────────┐  ││
│  │  │                                 ▼                                        │  ││
│  │  │  数据访问层 (Database)                                                  │  ││
│  │  │  ┌────────────────────────────────────────────────────────────────────┐  │  ││
│  │  │  │ MySQL: rules_v2, keyword_abilities_v2, ai_agent_pool, decks,       │  │  ││
│  │  │  │         ai_judge_daily_stats, feedbacks, homepage_card_config      │  │  ││
│  │  │  └────────────────────────────────────────────────────────────────────┘  │  ││
│  │  └─────────────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────┘
              │                                              │
              │ SSH + CLI                                   │
              ▼                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    自建服务器 (OpenCLAW Gateway)                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Docker 容器 (per-agent 隔离)                                                │ │
│  │  ├── openclaw agent CLI                                                   │ │
│  │  ├── Skill: mtg-judge                                                    │ │
│  │  ├── 知识库: workspace/skills/ai_judge/markdown/                          │ │
│  │  │   ├── 万智牌规则 1-9 章 (中文)                                           │ │
│  │  │   ├── 术语表 (glossarycn.md)                                            │ │
│  │  │   └── references/ (堆叠、触发式异能等)                                   │ │
│  │  └── LLM: MiniMax API                                                     │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 三层架构详解

### 3.1 客户端层

| 组件 | 说明 | 入口文件 |
|-----|------|---------|
| 微信小程序 | 用户交互界面，卡牌搜索、套牌管理、AI 对话 | miniprogram/app.js |
| 微信公众号 | 消息交互，规则问答快捷入口 | 消息处理见 wechat/handlers.py |

### 3.2 服务层

**云函数 (CloudBase Functions)**

| 配置项 | 值 |
|-------|-----|
| 函数名 | mtgAsk |
| 运行时 | Python 3.10 |
| 入口 | index.main |
| 超时 | 300 秒 |
| 内存 | 512 MB |

**服务模块**

| 模块 | 文件 | 职责 |
|-----|------|------|
| 路由层 | routes.py | FastAPI 路由定义，所有 API 端点 |
| 规则服务 | services/rule_service.py | 规则搜索、关键词异能查询 |
| 卡牌服务 | services/mtgch_api.py | MTGCH API 集成，卡牌搜索 |
| AI 裁判 | services/ai_judge_service.py | AI 对话、每日限制、会话管理 |
| Agent 池 | services/agent_pool_manager.py | per-user agent 生命周期管理 |
| OpenCLAW | services/openclaw_client.py | SSH 客户端，Gateway 通信 |
| 日志服务 | services/log_service.py | 统一日志（本地文件 + MySQL） |
| 定时任务 | services/scheduler.py | 规则自动更新调度 |

### 3.3 数据层

**MySQL 数据库表**

| 表名 | 用途 |
|-----|------|
| rules_v2 | 万智牌综合规则（中英文） |
| keyword_abilities_v2 | 关键词异能解释 |
| ai_agent_pool | AI Agent 与用户 openid 绑定 |
| ai_judge_daily_stats | 用户每日 AI 问答次数统计 |
| decks | 用户套牌存储 |
| feedbacks | 用户反馈 |
| homepage_card_config | 首页卡片显示配置 |

**外部数据源**

| 数据源 | 用途 |
|-------|------|
| MTGCH API | 卡牌数据查询（mtgch.com/api/v1） |
| Scryfall API | Promo 卡、Secret Lair 卡（api.scryfall.com） |
| Wizards of Coast | 官方规则 PDF 下载 |

---

## 4. 目录结构

```
mtgAsk/
├── functions/mtgAsk/                    # CloudBase 云函数
│   ├── backend/
│   │   ├── config.py                   # 配置管理（Config 类）
│   │   ├── database.py                # MySQL 数据访问层
│   │   ├── routes.py                  # FastAPI 路由（1200+ 行）
│   │   ├── main.py                    # 本地开发入口
│   │   │
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── rule_service.py        # 规则查询
│   │   │   ├── rule_downloader.py     # 规则下载
│   │   │   ├── card_service.py       # 卡牌服务
│   │   │   ├── card_downloader.py    # 卡牌下载
│   │   │   ├── mtgch_api.py          # MTGCH API 客户端
│   │   │   ├── ai_judge_service.py   # AI 裁判服务
│   │   │   ├── openclaw_client.py    # OpenCLAW SSH 客户端
│   │   │   ├── agent_pool_manager.py # Agent 池管理
│   │   │   ├── scheduler.py          # 定时任务调度
│   │   │   └── log_service.py       # 统一日志服务
│   │   │
│   │   ├── wechat/                    # 微信消息处理
│   │   │   └── handlers.py           # MessageHandler 类
│   │   │
│   │   ├── scripts/                   # 管理脚本
│   │   │   ├── import_rules.py
│   │   │   ├── import_en_v2.py
│   │   │   └── import_english_keywords.py
│   │   │
│   │   └── data/                      # 本地数据
│   │       └── magic-comp-rules-zh-cn-agent/  # AI 裁判知识库
│   │
│   ├── index.py                       # 云函数入口（简化版）
│   ├── scf_index.py                   # 云函数入口（旧版）
│   ├── requirements.txt               # 依赖列表
│   ├── scf_bootstrap                  # 云函数启动脚本
│   └── vendor/                        # 依赖包（Event 类型云函数）
│
├── miniprogram/                        # 微信小程序
│   ├── app.js                         # 小程序入口
│   ├── app.json                       # 全局配置
│   ├── pages/                         # 页面目录
│   │   ├── index/                    # 首页
│   │   ├── search/                   # 搜索页
│   │   ├── card/                     # 卡牌详情
│   │   ├── rule/                     # 规则详情
│   │   ├── keyword/                  # 关键词异能
│   │   ├── decks/                   # 套牌列表
│   │   ├── deck-detail/             # 套牌详情
│   │   ├── token/                   # Token 生成器
│   │   ├── promos/                  # Promo 卡快讯
│   │   ├── counter/                 # 生命值计数器
│   │   ├── dice/                   # 骰子 & 随机
│   │   ├── sldcards/               # Secret Lair 专区
│   │   └── apitest/                # API 测试页
│   ├── components/                    # 组件
│   └── images/                       # 图片资源
│
├── tests/                              # 测试代码
│   ├── unit/                         # 单元测试
│   ├── integration/                  # 集成测试
│   ├── cloud/                        # 云函数测试
│   └── conftest.py                   # pytest 配置
│
├── docs/                               # 项目文档
│   ├── ARCHITECTURE.md               # 架构文档
│   ├── MTGCH API接入说明.md          # MTGCH API 文档
│   ├── Scryfall API接入说明.md       # Scryfall API 文档
│   └── troubleshooting.md            # 故障排查
│
├── cloudbaserc.json                   # CloudBase 配置
├── deploy.sh                          # 部署脚本
└── requirements.txt                   # 依赖列表
```

---

## 5. 关键技术设计

### 5.1 环境检测与数据库切换

`database.py` 通过检测环境变量自动选择数据库：

```python
def _is_cloud_function(self) -> bool:
    cloud_env_indicators = [
        'SCF_FUNCTION_NAME',      # 腾讯云云函数
        'TENCENTCLOUD_RUNENV',    # 腾讯云运行环境
        'FC_REQUEST_ID',          # 阿里云函数计算
        'AWS_LAMBDA_FUNCTION_VERSION',  # AWS Lambda
    ]
    for indicator in cloud_env_indicators:
        if os.environ.get(indicator):
            return True
    return False
```

- **云函数环境**：使用环境变量中的外网 MySQL 地址（云函数无法访问内网 VPC）
- **本地环境**：使用 `.env.local` 配置或环境变量

### 5.2 per-user Agent 隔离

AI 裁判为每个微信用户分配独立 Agent：

```
用户 openid → ai_agent_pool 表 → agent_name → OpenCLAW Agent 容器
```

- Agent 池管理器 (`agent_pool_manager.py`) 维护 openid 与 agent_name 映射
- 空闲超时 30 分钟后标记为可回收，最大 100 个 Agent
- 定时清理过期会话和空闲 Agent

### 5.3 微信消息路由

消息处理器 (`wechat/handlers.py`) 支持：

| 前缀 | 处理函数 | 说明 |
|-----|---------|------|
| `卡牌:` / `card:` | `_handle_card_query` | MTGCH API 查询卡牌 |
| `异能:` / `ability:` | `_handle_keyword_query` | 关键词异能查询 |
| `裁判:` / `judge:` | `_handle_ai_judge_query` | AI 裁判对话 |
| `/help` | `_get_help_message` | 帮助信息 |
| `/start` | `_get_welcome_message` | 欢迎消息 |
| 其他文本 | `_handle_rule_search` | 规则综合搜索 |

### 5.4 统一日志服务

`log_service.py` 提供本地文件和 MySQL 双写：

```python
# 本地日志（云函数写 /tmp/logs/，本地写 logs/）
# MySQL 日志（ai_judge_logs 表）
log_info("service_name", "message", {"optional_data": "value"})
log_error("service_name", "error_message", {"error": details})
```

---

## 6. 部署拓扑

```
互联网
   │
   ├──► 微信小程序 ──────────────► HTTPS API ──► CloudBase 云函数 mtgAsk
   │                                                      │
   │                                                      ▼
   ├──► 微信公众号 ───► 微信服务器 ──► POST /wechat ──► │
   │                                                      │
   │                                               ┌──────┴────────┐
   │                                               ▼               ▼
   │                                         MySQL DB      OpenCLAW Gateway
   │                                                          │
   │                                                     ┌─────┴─────┐
   │                                                     ▼           ▼
   │                                              MiniMax API   Agent 容器
   │                                              (LLM)        (per-user)
   │
   └──► Scryfall API ───────────────────────────────────────────►│
                                                             
   └──► MTGCH API ───────────────────────────────────────────►│
```

---

## 7. 相关文档索引

| 文档 | 内容 |
|-----|------|
| [详细设计](DETAILED_DESIGN.md) | API 规范、数据库 schema、服务设计 |
| [测试文档](TESTING.md) | 测试策略、单元测试、集成测试 |
| [部署方案](DEPLOYMENT.md) | CloudBase 部署、配置管理、回滚 |
| [MTGCH API 接入说明](../docs/MTGCH%20API接入说明.md) | MTGCH API 使用详解 |
| [故障排查](../docs/troubleshooting.md) | 常见问题与解决方案 |

---

*文档版本: 1.0*
*最后更新: 2026-05-27*