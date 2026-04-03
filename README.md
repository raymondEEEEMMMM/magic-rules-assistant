# mtgAsk - 万智牌规则智能问答助手

<p align="center">
  <img src="miniprogram/images/mtgask_logo.png" width="200" alt="mtgAsk Logo"/>
</p>

<p align="center">
  <a href="https://github.com/raymondEEEEMMMM/magic-rules-assistant/blob/dev/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"/>
  </a>
  <a href="https://github.com/raymondEEEEMMMM/magic-rules-assistant/issues">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"/>
  </a>
</p>

## 项目简介

mtgAsk 是一个基于**微信小程序 + CloudBase 云函数**的万智牌（Magic: The Gathering）规则智能问答系统，帮助牌手快速查询卡牌信息、规则条款和理解万智牌规则。

### 核心功能

- **规则查询**：基于万智牌官方综合规则的智能搜索
- **卡牌搜索**：支持中英文卡牌名称搜索、原版优先排序
- **关键词异能**：快速查询 Flying、Trample 等异能解释
- **Secret Lair 专区**：浏览和搜索 SLD 系列卡牌
- **系列卡牌浏览**：按系列查看卡牌列表
- **AI 裁判**（可选）：基于大模型的复杂规则场景分析

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | Python + FastAPI | 云函数业务逻辑 |
| 数据库 | SQLite (本地) / MySQL (云端) | 规则和用户数据存储 |
| AI 服务 | MiniMax API + OpenCLAW Gateway | AI 裁判功能（可选） |
| 前端 | 微信小程序原生 | 用户交互界面 |
| 部署 | CloudBase 云函数 + 云托管 | 后端服务部署 |
| 卡牌数据 | MTGCH API + Scryfall API | 卡牌信息查询 |

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+（用于小程序开发）
- 微信开发者工具
- Git

### 1. 克隆项目

```bash
git clone https://github.com/raymondEEEEMMMM/magic-rules-assistant.git
cd magic-rules-assistant
```

### 2. 配置后端

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 填写必要的配置
```

### 3. 启动后端（本地开发）

```bash
cd functions/mtgAsk
python backend/main.py
# 服务运行在 http://localhost:8000
```

### 4. 微信小程序开发

```bash
# 安装小程序依赖（如需要）
cd miniprogram
npm install

# 使用微信开发者工具打开 miniprogram 目录
# 设置编译模式：普通编译
# 填入 API 地址：http://localhost:8000（如需本地调试）
```

### 5. 部署到 CloudBase

```bash
# 1. 安装依赖到 vendor 目录（Event 类型云函数需要）
mkdir -p functions/mtgAsk/vendor
pip install --target functions/mtgAsk/vendor -r requirements.txt -q

# 2. 配置 CloudBase CLI
npm install -g @cloudbase/cli
tcb login  # 登录腾讯云账号

# 3. 部署云函数
bash deploy.sh

# 4. 测试云函数
tcb fn invoke mtgAsk --params '{"httpMethod":"GET","path":"/","queryString":""}'
```

## 项目结构

```
magic-rules-assistant/
├── functions/mtgAsk/           # CloudBase 云函数
│   ├── index.py                # 云函数入口
│   ├── backend/
│   │   ├── config.py          # 配置管理
│   │   ├── database.py         # 数据库访问层
│   │   ├── routes.py           # API 路由
│   │   └── services/           # 业务逻辑服务
│   │       ├── rule_service.py      # 规则查询
│   │       ├── card_service.py       # 卡牌服务
│   │       ├── mtgch_api.py         # MTGCH API
│   │       └── ai_judge_service.py  # AI 裁判
│   └── vendor/                  # Python 依赖
│
├── miniprogram/                 # 微信小程序
│   ├── pages/                   # 页面目录
│   │   ├── index/              # 首页
│   │   ├── search/             # 搜索页
│   │   ├── card/               # 卡牌详情
│   │   ├── rule/               # 规则详情
│   │   ├── keyword/            # 关键词异能
│   │   ├── setcards/           # 系列卡牌
│   │   └── sldcards/           # Secret Lair 专区
│   ├── utils/                   # 工具函数
│   └── images/                  # 图片资源
│
├── docs/                        # 项目文档
│   ├── ARCHITECTURE.md         # 架构文档
│   ├── MTGCH API接入说明.md     # MTGCH API 说明
│   └── Scryfall API接入说明.md  # Scryfall API 说明
│
├── tests/                       # 测试代码
├── deployment/                 # 部署脚本
├── CLAUDE.md                   # Claude Code 开发指南
├── README.md                   # 项目说明
├── SECURITY.md                 # 安全策略
├── LICENSE                     # MIT 许可证
└── .env.example                # 环境变量示例
```

## API 文档

### 基础端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /` | GET | 服务状态 |
| `GET /api/search?q=` | GET | 规则综合搜索 |
| `GET /api/keyword?k=` | GET | 关键词异能查询 |
| `GET /api/card?q=` | GET | 卡牌搜索 |
| `GET /api/mtgch/card?id=` | GET | 卡牌详情 |
| `GET /api/mtgch/sets` | GET | 系列列表 |
| `GET /api/mtgch/set/{code}/cards` | GET | 系列卡牌列表 |

### Secret Lair 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /api/secret-lair/cards?months=` | GET | SLD 卡牌列表（默认12个月） |
| `GET /api/secret-lair/search?code=` | GET | 按编号搜索 SLD 卡牌 |

### AI 裁判端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `POST /api/ai-judge/chat` | POST | AI 裁判对话 |
| `POST /api/ai-judge/clear` | POST | 清除会话 |
| `GET /api/ai-judge/status` | GET | 服务状态 |

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

## 配置说明

### 环境变量

详细配置请参考 [`.env.example`](.env.example) 文件。

关键配置项：

| 变量 | 说明 | 必填 |
|------|------|------|
| `WECHAT_TOKEN` | 微信验证 Token | 是 |
| `MYSQL_HOST` | MySQL 主机地址 | 是 |
| `MYSQL_PASSWORD` | MySQL 密码 | 是 |
| `MINIMAX_API_KEY` | MiniMax API Key（AI 裁判用） | 否 |

### 微信开发者工具配置

1. 打开微信开发者工具
2. 导入 `miniprogram` 目录
3. 在 `app.js` 中确认 API 地址
4. 使用游客模式预览

## 数据来源

| 数据源 | 用途 | 链接 |
|--------|------|------|
| MTGCH API | 卡牌搜索、自动补全 | https://mtgch.com/api/v1/docs |
| Scryfall API | 卡牌图片、系列信息 | https://scryfall.com/docs/api |
| Wizards of Coast | 官方规则文档 | https://media.wizards.com/2026/downloads/ |

## 外部项目

本项目使用了以下开源项目的数据：

- **MTG 裁判知识库**: [magic-comp-rules-zh-cn-agent](https://github.com/Kuuusoda/magic-comp-rules-zh-cn-agent) - 提供 AI 裁判技能和裁判知识库

## 贡献指南

欢迎提交 Pull Request 或创建 Issue！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开源许可

本项目基于 [MIT License](LICENSE) 开源。

## 致谢

- 万智牌规则由 [Wizards of the Coast](https://company.wizards.com/) 提供
- 卡牌数据感谢 [Scryfall](https://scryfall.com/) 和 [MTGCH](https://mtgch.com/) 提供 API
