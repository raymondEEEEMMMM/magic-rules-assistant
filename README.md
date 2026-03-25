# mtgAsk - 万智牌规则问答系统

## 项目简介

基于微信小程序 + CloudBase 云函数的万智牌规则智能问答系统，帮助牌手快速查询卡牌、规则和理解万智牌规则。支持 AI 裁判功能，可处理复杂的规则场景分析。

## ✅ 已完成功能

### 基础查询功能
- ✅ 关键词异能查询（如 Flying、Trample）
- ✅ 卡牌名称搜索（中英文，支持模糊匹配）
- ✅ 规则综合搜索
- ✅ 随机卡牌推荐
- ✅ 卡牌自动补全

### AI 裁判功能
- ✅ OpenCLAW Gateway 集成（部署于 CloudBase Run）
- ✅ Per-user Agent 隔离（基于微信 openid）
- ✅ Docker 沙箱隔离
- ✅ MTG 裁判 Persona（SOUL.md）
- ✅ MiniMax API 驱动
- ✅ 会话历史自动截断（保留最近 10 条）
- ✅ 定时会话清理（每 12 小时）
- ✅ 流式响应处理

### 数据与定时任务
- ✅ 自动下载最新规则（TXT 格式）
- ✅ 规则版本检查和增量更新
- ✅ 定时任务调度（每天 03:00、每周一 10:00）
- ✅ MTGCH API 卡牌数据集成

### 云端部署
- ✅ CloudBase 云函数部署（Event 类型，Python 3.10）
- ✅ CloudBase Run 部署（OpenCLAW Gateway）
- ✅ MySQL 数据库连接
- ✅ 微信小程序接入

## 📦 技术栈

- **后端**: Python + FastAPI
- **数据库**: SQLite (本地) / MySQL (云端)
- **AI**: OpenCLAW Gateway + MiniMax API
- **前端**: 微信小程序
- **部署**: CloudBase 云函数 + CloudBase Run

## 🏗️ 项目结构

```
cbworkplace/
├── functions/mtgAsk/        # CloudBase 云函数
│   ├── index.py             # 云函数入口
│   ├── backend/
│   │   ├── database.py      # 数据库操作
│   │   ├── config.py         # 配置管理
│   │   └── services/        # 业务逻辑
│   │       ├── rule_service.py      # 规则查询
│   │       ├── card_service.py      # 卡牌查询
│   │       ├── mtgch_api.py         # MTGCH API
│   │       ├── ai_judge_service.py  # AI 裁判
│   │       └── agent_pool_manager.py # Agent 池管理
│   └── vendor/              # 依赖包
├── miniprogram/             # 微信小程序
│   ├── pages/
│   │   ├── index/           # 首页
│   │   ├── search/          # 搜索页
│   │   ├── card/            # 卡牌详情
│   │   ├── agent/           # AI 裁判聊天
│   │   └── ...
│   └── utils/
│       └── api.js           # API 工具
├── deployment/              # 部署脚本
└── tests/                  # 测试
```

## 🚀 快速开始

### 本地运行后端

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp functions/mtgAsk/backend/.env.example functions/mtgAsk/backend/.env
# 编辑 .env 填写配置

# 4. 启动服务
cd functions/mtgAsk
python backend/main.py
# 服务运行在 http://localhost:8000
```

### 部署到 CloudBase

```bash
# 1. 安装依赖到 vendor 目录
mkdir -p functions/mtgAsk/vendor
pip install --target functions/mtgAsk/vendor -r requirements.txt -q

# 2. 部署云函数
bash deploy.sh

# 3. 测试云函数
tcb fn invoke mtgAsk --params '{"httpMethod":"GET","path":"/","queryString":""}'
```

## 📡 API 端点

### 基础端点
| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/api/search` | GET | 规则综合搜索 |
| `/api/keyword` | GET | 关键词异能查询 |
| `/api/rule` | GET | 规则详情查询 |
| `/api/card` | GET | 卡牌搜索 |
| `/api/mtgch/card` | GET | 卡牌详情 |
| `/api/mtgch/random` | GET | 随机卡牌 |
| `/api/mtgch/autocomplete` | GET | 卡牌自动补全 |

### AI 裁判端点
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/ai-judge/chat` | POST | AI 裁判对话 |
| `/api/ai-judge/clear` | POST | 清除会话 |

### 管理端点
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/admin/cleanup-sessions` | POST | 清理所有 OpenCLAW 会话 |
| `/api/admin/agent-pool/stats` | POST | Agent 池统计 |

### 测试示例

```bash
# 搜索规则
curl 'http://localhost:8000/api/search?q=opposition+agent'

# 搜索卡牌
curl 'http://localhost:8000/api/card?q=Lightning'

# AI 裁判对话
curl -X POST 'http://localhost:8000/api/ai-judge/chat' \
  -H 'Content-Type: application/json' \
  -d '{"message": "反对派密探的异能是什么？", "session_id": "test"}'
```

## 🤖 AI 裁判使用

AI 裁判基于 OpenCLAW Gateway 构建，部署在 CloudBase Run。

### 核心特性

- **Per-user Agent**: 每个用户有独立的 OpenCLAW Agent
- **会话隔离**: 基于 openid 的用户隔离
- **自动清理**: 每 12 小时自动清理过期会话
- **历史截断**: 保留最近 10 条消息，控制 token 消耗

### 对话示例

```
用户: 反对派密探的异能是什么？
AI:  反对派密探（Opposition Agent）的异能是：
     {2}{B}
     生物～人类/奥秘师
     警示（每当你将要使用一张地时，反对派密探上的警示异能各触发一次。）
     T：选择一项——将一个由你操控的非地永久物移回其拥有者手上；或者消灭由对手操控的一个鹏洛客。

用户: 那如果我有多个反对派密探呢？
AI:  如果场上有多个反对派密探，每个都有自己的警示异能...
```

## 🤝 合作伙伴

### MTG 裁判知识库
- **项目**: [magic-comp-rules-zh-cn-agent](https://github.com/Kuuusoda/magic-comp-rules-zh-cn-agent)
- **用途**: 提供 AI 裁判的技能（Skill）和裁判知识库
- **本地路径**: `functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/`

## 📝 许可证
MIT License
