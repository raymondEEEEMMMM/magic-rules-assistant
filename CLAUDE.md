# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mtgAsk is a WeChat-based Magic: The Gathering rule Q&A system that provides card lookups, keyword ability searches, and rule queries. It consists of a Python cloud function backend and a WeChat mini-program frontend.

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Backend
```bash
# Start local server (runs on localhost:8000)
python functions/mtgAsk/backend/main.py
# Or use the start script
bash deployment/scripts/start.sh
```

### Testing
```bash
# Test first stage features
python tests/integration/test_first_stage.py

# Test card service
python tests/integration/test_card_service.py

# Test cloud API
bash test_cloud_api.sh
```

### Testing API Endpoints
```bash
curl 'http://localhost:8000/api/search?q=飞行'
curl 'http://localhost:8000/api/card?n=黑莲花'
curl 'http://localhost:8000/api/keyword?k=践踏'
```

### Deployment
```bash
# 1. 复制虚拟环境到 vendor 目录（Event 类型云函数需要）
mkdir -p functions/mtgAsk/vendor
pip install --target functions/mtgAsk/vendor -r requirements.txt -q

# 2. 部署到 CloudBase
bash deploy.sh

# 3. 测试云函数
tcb fn invoke mtgAsk --params '{"httpMethod":"GET","path":"/","queryString":""}'
```
**注意**: Event 类型云函数需要将虚拟环境一起上传到 vendor 目录，并在 scf_bootstrap 中设置 PYTHONPATH。

## Architecture

### Three-Tier Architecture

1. **Client Layer**: WeChat Mini-program (`miniprogram/`) + WeChat Official Account
2. **Service Layer**: CloudBase Functions (`functions/mtgAsk/`) with FastAPI
3. **Data Layer**: MySQL database (CloudBase) with SQLite for local development

### Backend Structure

```
functions/mtgAsk/
├── index.py                    # Cloud function entry point (main)
├── backend/
│   ├── routes.py               # FastAPI routes definition
│   ├── database.py             # MySQL/SQLite data access layer
│   ├── config.py               # Configuration management
│   ├── services/
│   │   ├── rule_service.py     # Rule query logic
│   │   ├── card_service.py    # Card lookup logic
│   │   ├── rule_downloader.py # Download rules from Wizards of Coast
│   │   ├── card_downloader.py # Download card data from MTGJSON
│   │   ├── scheduler.py       # Scheduled tasks (03:00 daily, 10:00 Monday)
│   │   ├── mtgch_api.py       # MTGCH API integration
│   │   ├── ai_judge_service.py # AI Judge (OpenCLAW Gateway)
│   │   └── log_service.py     # Unified logging (local + MySQL)
│   └── wechat/
│       └── handlers.py         # WeChat message handling
```

### Frontend Structure

```
miniprogram/
├── pages/
│   ├── index/    # Home page
│   ├── search/   # Search page
│   ├── card/     # Card detail page
│   ├── rule/     # Rule detail page
│   ├── keyword/  # Keyword ability page
│   └── apitest/  # API testing page
└── app.js        # Mini-program entry, contains API base URL
```

### Database

- **Production**: MySQL on CloudBase (host: 172.17.0.5, port: 3306)
- **Development**: SQLite local file or external MySQL (config in `.env.local`)
- Auto-detects environment via `_is_cloud_function()` in `database.py`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/wechat` | GET/POST | WeChat verification/messages |
| `/api/search` | GET | Rule search |
| `/api/keyword` | GET | Keyword ability lookup |
| `/api/card` | GET | Card rule lookup |
| `/api/rules/update` | POST | Update rules from source |
| `/api/rules/status` | GET | Get rule version status |
| `/api/ai-judge/chat` | POST | AI Judge chat (支持 per-user agent 隔离) |
| `/api/ai-judge/clear` | POST | Clear AI Judge session |

### Cloud Function Configuration

Defined in `cloudbaserc.json`:
- Runtime: Python 3.10
- Handler: `index.main`
- Timeout: 60 seconds
- Memory: 512 MB

### CloudBase Run (OpenCLAW Gateway)

OpenCLAW Gateway is deployed on CloudBase Run for AI Judge functionality:

| Property | Value |
|----------|-------|
| Service Name | openclaw-gateway |
| URL | https://openclaw-gateway-233331-7-1410769303.sh.run.tcloudbase.com |
| Port | 18789 |
| CPU | 1 core |
| Memory | 2 GB |

Deploy OpenCLAW Gateway:
```bash
tcb run:deprecated version create \
  -e magic-rules-assistant-0a1904c329 \
  -s openclaw-gateway \
  -p . \
  --dockerFile cloudrun/openclaw-gateway/Dockerfile \
  --port 18789 \
  -c 1 \
  --mem 2
```

### Environment Variables

Key variables (in `.env.local` for local, `cloudbaserc.json` for cloud):
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- `WECHAT_TOKEN`
- `TCB_ENV_ID`
- `MINIMAX_API_KEY` - MiniMax API key (used by OpenCLAW Gateway)
- `OPENCLAW_ENABLED` - Enable OpenCLAW Gateway (default: true)
- `OPENCLAW_GATEWAY_URL` - OpenCLAW Gateway URL
- `OPENCLAW_SSH_USER`, `OPENCLAW_SSH_KEY_CONTENT` - SSH access to Gateway host
- `OPENCLAW_PORT` - SSH port (default: 22)

## Key Design Patterns

1. **Environment Detection**: `database.py` checks for cloud function indicators (`SCF_FUNCTION_NAME`, `TENCENTCLOUD_RUNENV`) to switch between MySQL (cloud) and SQLite (local)

2. **Service Layer**: Business logic isolated in `services/` directory, imported by `routes.py`

3. **WeChat Message Handling**: Text messages parsed and routed to appropriate handlers based on prefixes (`卡牌:`, `异能:`) or commands (`/help`, `/start`)

4. **Scheduled Updates**: `scheduler.py` runs periodic rule updates using the `schedule` library

## Partner Projects

### MTG 裁判知识库
- **Repo**: https://github.com/Kuuusoda/magic-comp-rules-zh-cn-agent
- **用途**: 提供 AI 裁判的技能（Skill）和裁判知识库
- **本地路径**: `functions/mtgAsk/backend/data/magic-comp-rules-zh-cn-agent/`
- **说明**: 包含万智牌规则的中英文版本、关键词解释、参考文档等

## Important Files

- `functions/mtgAsk/index.py` - Cloud function entry point
- `functions/mtgAsk/backend/routes.py` - All API route definitions
- `functions/mtgAsk/backend/database.py` - Database connection management
- `miniprogram/app.js` - Mini-program config with API base URL
- `cloudbaserc.json` - CloudBase deployment configuration

## Future Plans

### Completed Features

### Unified Logging Service ✅
- Log service: `backend/services/log_service.py`
- Supports local file logs (`/tmp/logs/` in cloud, `logs/` locally)
- Supports MySQL database logs (`ai_judge_logs` table)
- Usage:
  ```python
  from backend.services.log_service import log_info, log_warning, log_error
  log_info("service_name", "message", {"data": "optional"})
  ```

### AI Judge Feature (Phase 2) ✅
- Integrated OpenCLAW Gateway for AI-powered rule Q&A
- Uses ai_judge skill with MiniMax API
- Chat interface: `POST /api/ai-judge/chat`
- Per-user agent isolation: each user gets independent OpenCLAW agent
- Agent workspace: `/home/openclaw/agents/user_{sanitized_openid}`
- Docker sandbox auto-creates containers per agent
- Gateway deployed on CloudBase Run: `https://openclaw-gateway-233331-7-1410769303.sh.run.tcloudbase.com`

### Upcoming Features
- Card image lookup integration
- Multi-language support
