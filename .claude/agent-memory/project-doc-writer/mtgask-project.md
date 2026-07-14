---
name: mtgask-project-structure
description: mtgAsk is a WeChat Mini-Program + CloudBase Cloud Function MTG rule Q&A system
metadata:
  type: project
---

# mtgAsk Project Context

## Project Overview
mtgAsk is a Magic: The Gathering rule Q&A system with:
- **Frontend**: WeChat Mini-Program (miniprogram/)
- **Backend**: CloudBase Python cloud functions (functions/mtgAsk/)
- **Database**: CloudBase MySQL (外网地址: sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com:27987)
- **AI Judge**: OpenCLAW Gateway on self-hosted server with Docker, using MiniMax API

## Key Features (as of 2026-05-27)
1. Card search via MTGCH API (mtgch.com/api/v1)
2. Rule search with keyword abilities lookup
3. AI Judge with per-user agent isolation
4. Deck management (list, add, delete, update, parse URL, calc CMC)
5. Token generator, Promo cards, Secret Lair cards
6. Scheduled rule updates (03:00 daily, 10:00 Monday)

## Important Files
- `functions/mtgAsk/index.py` - Cloud function entry point
- `functions/mtgAsk/backend/routes.py` - FastAPI routes (1200+ lines)
- `functions/mtgAsk/backend/database.py` - MySQL data access layer
- `functions/mtgAsk/backend/services/ai_judge_service.py` - AI Judge service
- `functions/mtgAsk/backend/services/mtgch_api.py` - MTGCH API client

## CloudBase Configuration
- Function: mtgAsk, Python 3.10, 512MB, 300s timeout
- Handler: index.main
- envId: magic-rules-assistant-0a1904c329

## No Official Account
- The project previously had WeChat Official Account (微信公众号) integration
- As of current state, only Mini-Program frontend remains
- WeChat message endpoint `/wechat` is still present but not actively used

## Testing
- Unit tests: 78 tests passing (pytest + mock)
- Test files in `tests/unit/`, `tests/integration/`, `tests/cloud/`
- Some tests blocked by starlette/httpx incompatibility