from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import XMLResponse, StreamingResponse, PlainTextResponse
from typing import Optional
import hashlib
import re
import requests
from database import RuleDatabase
from services import RuleService
from wechat import MessageHandler
from config import Config

# 初始化数据库和服务
db = RuleDatabase()
rule_service = RuleService(db)
message_handler = MessageHandler(rule_service)

# 初始化调度器（延迟导入避免启动失败）
rule_scheduler = None

app = FastAPI(title="万智牌规则问答API")

def verify_wechat_signature(timestamp: str, nonce: str, signature: str) -> bool:
    """验证微信签名"""
    params = [Config.WECHAT_TOKEN, timestamp, nonce]
    params.sort()
    params_str = "".join(params)
    sha1 = hashlib.sha1()
    sha1.update(params_str.encode("utf-8"))
    return sha1.hexdigest() == signature

@app.get("/")
async def root():
    return {"message": "万智牌规则问答服务运行中", "status": "ok"}

@app.get("/wechat", response_class=PlainTextResponse)
async def wechat_verify(
    signature: str,
    timestamp: str,
    nonce: str,
    echostr: str
):
    """微信服务器验证"""
    if verify_wechat_signature(timestamp, nonce, signature):
        return echostr
    else:
        raise HTTPException(status_code=403, detail="签名验证失败")

def create_xml_response(content: str, to_user: str, from_user: str) -> str:
    """创建XML响应"""
    return f"""
    <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime>{int(__import__("time").time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>
    """

@app.post("/wechat")
async def wechat_message(request: Request):
    """处理微信消息"""
    body = await request.body()
    import xml.etree.ElementTree as ET
    root = ET.fromstring(body)

    msg_type = root.find("MsgType").text
    from_user = root.find("FromUserName").text
    to_user = root.find("ToUserName").text

    # 处理事件消息
    if msg_type == "event":
        event = root.find("Event").text
        response = message_handler.handle_event(event)
        if response:
            return XMLResponse(content=create_xml_response(response, from_user, to_user))
        return XMLResponse(content="")

    # 处理文本消息
    elif msg_type == "text":
        user_message = root.find("Content").text
        response = message_handler.handle_text_message(user_message)
        return XMLResponse(content=create_xml_response(response, from_user, to_user))

    return XMLResponse(content="")

@app.get("/api/search")
async def search_rules(q: str):
    """规则搜索API"""
    results = rule_service.search_rules(q)
    return {"query": q, "results": results}

@app.get("/api/keyword")
async def get_keyword_ability(keyword: str):
    """获取关键词异能API"""
    result = rule_service.get_keyword_ability(keyword)
    if result:
        return {"keyword": keyword, "result": result}
    return {"keyword": keyword, "result": None}

@app.get("/api/card")
async def get_card_rule(card_name: str, order: str = "releaseDate"):
    """获取卡牌规则API - 使用 MTGCH API，按发行日期排序返回原版优先"""
    try:
        from services.mtgch_api import MTGCHAPIClient
        client = MTGCHAPIClient(timeout=30)
        result = client.search_cards(card_name, page=1, page_size=5, order=order)
        client.close()
        return result  # MTGCH API 返回 {items: [...], total: ...}
    except Exception as e:
        return {"items": [], "total": 0, "error": str(e)}

# ==================== 微信 HTTP 访问路径 API ====================
# 这些路由用于 HTTP 访问路径 /wechat 的调用

@app.get("/wechat/api/search")
async def wechat_search_rules(q: str):
    """规则搜索API - 微信HTTP访问"""
    results = rule_service.search_rules(q)
    return {"query": q, "results": results}

@app.get("/wechat/api/keyword")
async def wechat_get_keyword_ability(k: str):
    """获取关键词异能API - 微信HTTP访问"""
    result = rule_service.get_keyword_ability(k)
    if result:
        return {"keyword": k, "result": result}
    return {"keyword": k, "result": None}

@app.get("/wechat/api/mtgch/search")
async def wechat_mtgch_search(q: str, page: int = 1, page_size: int = 5, priority_chinese: bool = True):
    """MTGCH 卡牌搜索API - 微信HTTP访问"""
    try:
        from services.mtgch_api import MTGCHAPIClient
        client = MTGCHAPIClient(timeout=30)
        result = client.search_cards(
            q,
            page=page,
            page_size=page_size,
            priority_chinese=priority_chinese
        )
        client.close()
        return result
    except Exception as e:
        return {"error": str(e), "items": [], "total": 0}

@app.get("/wechat/api/mtgch/random")
async def wechat_mtgch_random():
    """MTGCH 随机卡牌API - 微信HTTP访问"""
    try:
        from services.mtgch_api import MTGCHAPIClient
        client = MTGCHAPIClient(timeout=30)
        result = client.get_random_card()
        client.close()
        return result if result else {"error": "No card found"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/wechat/api/mtgch/autocomplete")
async def wechat_mtgch_autocomplete(q: str, size: int = 10):
    """MTGCH 自动补全API - 微信HTTP访问"""
    try:
        from services.mtgch_api import MTGCHAPIClient
        client = MTGCHAPIClient(timeout=30)
        result = client.autocomplete(q, size=size)
        client.close()
        return result
    except Exception as e:
        return {"error": str(e), "items": [], "suggestions": []}

@app.get("/wechat/api/mtgch/card")
async def wechat_mtgch_card(id: str = None, set: str = None, number: str = None):
    """MTGCH 卡牌详情API - 微信HTTP访问"""
    try:
        from services.mtgch_api import MTGCHAPIClient
        client = MTGCHAPIClient(timeout=30)

        if id:
            result = client.get_card_by_id(id)
        elif set and number:
            result = client.get_card_by_set_and_number(set, number)
        else:
            return {"error": "Missing id or set+number parameters"}

        client.close()
        return result if result else {"error": "Card not found"}
    except Exception as e:
        return {"error": str(e)}

# ==================== 规则下载相关 API ====================

@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global rule_scheduler
    try:
        from services.scheduler import rule_scheduler as rs, on_rules_update
        rule_scheduler = rs
        rule_scheduler.set_update_callback(on_rules_update)
        rule_scheduler.start()
        print("✓ 规则更新调度器已启动")
    except Exception as e:
        print(f"⚠ 调度器启动失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    global rule_scheduler
    if rule_scheduler:
        rule_scheduler.stop()
        print("✓ 规则更新调度器已停止")

@app.post("/api/rules/update")
async def update_rules(background_tasks: BackgroundTasks, force: bool = False):
    """
    更新规则

    Args:
        force: 是否强制更新（忽略本地缓存）
    """
    try:
        from services.rule_downloader import RuleDownloader

        downloader = RuleDownloader()
        result = downloader.download_rules(force=force)

        return {
            "success": result["success"],
            "message": result.get("message"),
            "version": result.get("version"),
            "date": result.get("date")
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"更新失败: {str(e)}"
        }

@app.get("/api/rules/parse")
async def parse_rules():
    """解析规则文件"""
    try:
        from services.rule_downloader import RuleDownloader

        downloader = RuleDownloader()
        result = downloader.parse_rules()

        if result["success"]:
            return {
                "success": True,
                "rules_count": len(result["rules"]),
                "keyword_count": len(result["keyword_abilities"]),
                "glossary_count": len(result["glossary"]),
                "data": {
                    "rules_sample": result["rules"][:3] if result["rules"] else [],
                    "keywords_sample": result["keyword_abilities"][:3] if result["keyword_abilities"] else []
                }
            }
        else:
            return {
                "success": False,
                "message": result.get("message")
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"解析失败: {str(e)}"
        }

@app.get("/api/rules/vectorization")
async def get_rules_for_vectorization():
    """获取适合向量化的规则数据"""
    try:
        from services.rule_downloader import RuleDownloader

        downloader = RuleDownloader()
        result = downloader.get_rules_for_vectorization()

        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"获取失败: {str(e)}"
        }

@app.get("/api/rules/status")
async def get_rules_status():
    """获取规则状态"""
    try:
        from services.rule_downloader import RuleDownloader

        downloader = RuleDownloader()

        # 获取本地规则信息
        local_info = downloader._get_local_rules_info()

        # 获取在线规则信息
        online_info = downloader._get_online_rules_info()

        # 获取调度器状态
        scheduler_status = {}
        if rule_scheduler:
            scheduler_status = rule_scheduler.get_status()

        return {
            "success": True,
            "local_version": local_info.get("version") if local_info else None,
            "local_date": local_info.get("date") if local_info else None,
            "online_version": online_info.get("version") if online_info else None,
            "online_date": online_info.get("date") if online_info else None,
            "is_latest": downloader._is_latest_version(local_info, online_info) if local_info and online_info else None,
            "scheduler": scheduler_status
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"获取状态失败: {str(e)}"
        }

# ==================== AI 裁判 API ====================

@app.post("/api/ai-judge/init")
async def ai_judge_init(request: Request):
    """预热 AI Agent

    参数:
    - openid: 微信 openid (必填，用于 per-user agent 隔离)

    作用:
    - 提前创建/获取用户的 Agent
    - 减少用户首次发送消息时的等待时间
    """
    body = await request.json()
    openid = body.get("openid", None)

    if not openid:
        return {"success": False, "error": "openid is required"}

    from services.ai_judge_service import ai_judge_service
    result = ai_judge_service.init_agent(openid=openid)
    return result

@app.post("/api/ai-judge/chat")
async def ai_judge_chat(request: Request):
    """与 AI 裁判对话

    参数:
    - message: 用户消息
    - session_id: 会话ID (默认: default)
    - clear_history: 是否清除历史 (默认: false)
    - short_mode: 是否使用简短模式 (默认: false, 减少 token 消耗)
    - openid: 微信 openid (可选，用于 per-user agent 隔离)
    """
    body = await request.json()
    message = body.get("message", "")
    session_id = body.get("session_id", "default")
    clear_history = body.get("clear_history", False)
    short_mode = body.get("short_mode", False)
    openid = body.get("openid", None)

    if not message:
        return {"success": False, "reply": "消息不能为空"}

    from services.ai_judge_service import ai_judge_service

    # 如果请求清除历史
    if clear_history:
        ai_judge_service.clear_session(session_id)

    result = ai_judge_service.chat(message, session_id, short_mode=short_mode, openid=openid)
    return result


@app.post("/api/ai-judge/analyze")
async def ai_judge_analyze(request: Request):
    """AI 裁判分析对局"""
    body = await request.json()
    game_state = body.get("game_state", "")
    cards = body.get("cards", [])
    question = body.get("question", "")

    if not game_state and not question:
        return {"success": False, "analysis": "请提供对局描述或问题"}

    from services.ai_judge_service import ai_judge_service
    result = ai_judge_service.analyze({
        "game_state": game_state,
        "cards": cards,
        "question": question
    })
    return result

@app.post("/api/ai-judge/clear")
async def ai_judge_clear_session(request: Request):
    """清除 AI 裁判会话历史"""
    body = await request.json()
    session_id = body.get("session_id", "default")
    openid = body.get("openid", None)

    from services.ai_judge_service import ai_judge_service

    # 获取 agent_name - 使用模块级 db 实例
    agent_name = None
    if openid:
        agent_info = db.get_agent_by_openid(openid)
        if agent_info:
            agent_name = agent_info.get("agent_name")

    ai_judge_service.clear_session(session_id, agent_name=agent_name)
    return {"success": True, "message": "会话已清除"}

# ==================== 微信 HTTP 访问路径 AI 裁判 API ====================

@app.post("/wechat/api/ai-judge/chat")
async def wechat_ai_judge_chat(request: Request):
    """与 AI 裁判对话 - 微信HTTP访问

    参数:
    - message: 用户消息
    - session_id: 会话ID (默认: default)
    - clear_history: 是否清除历史 (默认: false)
    - short_mode: 是否使用简短模式 (默认: false)
    - openid: 微信 openid (可选，用于 per-user agent 隔离)
    """
    body = await request.json()
    message = body.get("message", "")
    session_id = body.get("session_id", "default")
    clear_history = body.get("clear_history", False)
    short_mode = body.get("short_mode", False)
    openid = body.get("openid", None)

    if not message:
        return {"success": False, "reply": "消息不能为空"}

    from services.ai_judge_service import ai_judge_service

    if clear_history:
        ai_judge_service.clear_session(session_id)

    result = ai_judge_service.chat(message, session_id, short_mode=short_mode, openid=openid)
    return result


@app.post("/wechat/api/ai-judge/new-session")
async def wechat_ai_judge_new_session(request: Request):
    """创建新会话 - 微信HTTP访问"""
    body = await request.json()
    session_id = body.get("session_id", "default")
    reset_agent = body.get("reset_agent", True)

    from services.ai_judge_service import ai_judge_service
    result = ai_judge_service.new_session(session_id, reset_agent)
    return result


@app.post("/wechat/api/ai-judge/clear")
async def wechat_ai_judge_clear_session(request: Request):
    """清除会话 - 微信HTTP访问"""
    body = await request.json()
    session_id = body.get("session_id", "default")
    openid = body.get("openid", None)

    from services.ai_judge_service import ai_judge_service
    from database import db

    # 获取 agent_name
    agent_name = None
    if openid:
        agent_info = db.get_agent_by_openid(openid)
        if agent_info:
            agent_name = agent_info.get("agent_name")

    ai_judge_service.clear_session(session_id, agent_name=agent_name)
    return {"success": True, "message": "会话已清除"}


@app.get("/wechat/api/ai-judge/history")
async def wechat_get_ai_judge_history(
    request: Request,
    openid: str = None,
    limit: int = 10,
    offset: int = 0,
    session_id: str = None
):
    """
    获取 AI 裁判会话历史 - 微信HTTP访问

    参数和使用方式与 /api/ai-judge/history 相同
    """
    return await get_ai_judge_history(request, openid, limit, offset, session_id)


@app.post("/api/ai-judge/new-session")
async def ai_judge_new_session(
    session_id: str = "default",
    reset_agent: bool = True
):
    """
    创建新会话

    清除当前会话历史并可选重置 OpenCLAW Agent
    """
    from services.ai_judge_service import ai_judge_service
    result = ai_judge_service.new_session(session_id, reset_agent)
    return result


@app.get("/api/ai-judge/history")
async def get_ai_judge_history(
    request: Request,
    openid: str = None,
    limit: int = 10,
    offset: int = 0,
    session_id: str = None
):
    """
    获取 AI 裁判会话历史

    - 不传 session_id: 返回会话列表
    - 传 session_id: 返回该会话的消息历史

    请求参数:
    - openid (必填): 用户 openid
    - limit (可选, 默认10): 会话数量上限
    - offset (可选, 默认0): 分页偏移
    - session_id (可选): 指定会话 ID
    """
    if not openid:
        return {"success": False, "error": {"code": "MISSING_OPENID", "message": "openid 参数必填"}}

    try:
        from services.agent_pool_manager import AgentPoolManager
        from services.openclaw_client import OpenCLAWClient

        # 获取用户的 agent 名称
        agent_manager = AgentPoolManager()
        agent_info = agent_manager.db.get_agent_by_openid(openid)

        if not agent_info:
            return {"success": False, "error": {"code": "AGENT_NOT_FOUND", "message": "未找到该用户的会话记录"}}

        agent_name = agent_info["agent_name"]

    except Exception as e:
        return {"success": False, "error": {"code": "DB_ERROR", "message": str(e)}}

    try:
        client = OpenCLAWClient()

        if session_id:
            # 返回指定会话的消息
            messages = client.get_session_messages(agent_name, session_id, limit=limit)

            # 统计
            user_count = sum(1 for m in messages if m.get("role") == "user")
            assistant_count = sum(1 for m in messages if m.get("role") == "assistant")

            return {
                "success": True,
                "data": {
                    "sessionId": session_id,
                    "messages": messages,
                    "summary": {
                        "totalMessages": len(messages),
                        "userMessages": user_count,
                        "assistantMessages": assistant_count
                    }
                }
            }
        else:
            # 返回会话列表
            result = client.get_sessions(agent_name, limit=limit, offset=offset)
            return {
                "success": True,
                "data": result
            }

    except Exception as e:
        return {"success": False, "error": {"code": "SSH_ERROR", "message": str(e)}}


@app.post("/api/ai-judge/history")
async def post_ai_judge_history(request: Request):
    """
    获取 AI 裁判会话历史 - POST 版本（小程序客户端用）

    请求体 (JSON):
    - openid (必填): 用户 openid
    - limit (可选, 默认10): 会话数量上限
    - offset (可选, 默认0): 分页偏移
    - session_id (可选): 指定会话 ID
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": {"code": "INVALID_JSON", "message": "请求体必须是有效 JSON"}}

    openid = body.get("openid")
    limit = body.get("limit", 10)
    offset = body.get("offset", 0)
    session_id = body.get("session_id")

    if not openid:
        return {"success": False, "error": {"code": "MISSING_OPENID", "message": "openid 参数必填"}}

    try:
        from services.agent_pool_manager import AgentPoolManager
        from services.openclaw_client import OpenCLAWClient

        agent_manager = AgentPoolManager()
        agent_info = agent_manager.db.get_agent_by_openid(openid)

        if not agent_info:
            return {"success": False, "error": {"code": "AGENT_NOT_FOUND", "message": "未找到该用户的会话记录"}}

        agent_name = agent_info["agent_name"]

    except Exception as e:
        return {"success": False, "error": {"code": "DB_ERROR", "message": str(e)}}

    try:
        client = OpenCLAWClient()

        if session_id:
            messages = client.get_session_messages(agent_name, session_id, limit=limit)
            user_count = sum(1 for m in messages if m.get("role") == "user")
            assistant_count = sum(1 for m in messages if m.get("role") == "assistant")
            return {
                "success": True,
                "data": {
                    "sessionId": session_id,
                    "messages": messages,
                    "summary": {
                        "totalMessages": len(messages),
                        "userMessages": user_count,
                        "assistantMessages": assistant_count
                    }
                }
            }
        else:
            result = client.get_sessions(agent_name, limit=limit, offset=offset)
            return {
                "success": True,
                "data": result
            }

    except Exception as e:
        return {"success": False, "error": {"code": "SSH_ERROR", "message": str(e)}}


# ==================== 微信 HTTP 访问路径 AI 裁判 API ====================

@app.post("/api/feedback")
async def submit_feedback(request: Request):
    """
    提交用户反馈

    请求体:
    {
        "content": "反馈内容",
        "contact": "联系方式(可选)",
        "type": "suggestion" | "bug" | "other"
    }
    """
    body = await request.json()
    content = body.get("content", "")
    contact = body.get("contact")
    feedback_type = body.get("type", "suggestion")

    if not content:
        return {"success": False, "message": "反馈内容不能为空"}

    # 获取用户 openid
    openid = body.get("openid") or request.headers.get("X-WX-Openid")

    if not openid:
        return {"success": False, "message": "无法获取用户身份"}

    success = db.submit_feedback(openid, content, contact, feedback_type)

    if success:
        return {"success": True, "message": "反馈已提交"}
    else:
        return {"success": False, "message": "反馈提交失败"}


# ==================== 管理 API ====================

@app.post("/api/admin/cleanup-sessions")
async def admin_cleanup_sessions():
    """
    清理所有 OpenCLAW 过期会话

    调用 openclaw sessions cleanup --enforce 清理累积的会话历史
    """
    from services.agent_pool_manager import AgentPoolManager

    manager = AgentPoolManager()
    result = manager.cleanup_all_sessions()
    return result


@app.post("/api/admin/agent-pool/stats")
async def admin_agent_pool_stats():
    """
    获取 Agent 池统计信息
    """
    from services.agent_pool_manager import AgentPoolManager

    manager = AgentPoolManager()
    stats = manager.get_pool_stats()
    return {"success": True, "stats": stats}


# ==================== 套牌 API ====================

import httpx
import time

# 简单的内存缓存 (key: card_name_lower, value: (cmc, timestamp))
_cmc_cache: dict[str, tuple[float, float]] = {}
_CACHE_TTL = 7 * 24 * 60 * 60  # 7天过期
_LAST_REQUEST_TIME = 0.0
_MIN_REQUEST_INTERVAL = 0.1  # 最小请求间隔 100ms (10 req/s)


def _clean_expired_cache():
    """清理过期缓存"""
    global _cmc_cache
    now = time.time()
    expired = [k for k, v in _cmc_cache.items() if now - v[1] > _CACHE_TTL]
    for k in expired:
        del _cmc_cache[k]


def _rate_limit():
    """简单的速率限制"""
    global _LAST_REQUEST_TIME
    now = time.time()
    elapsed = now - _LAST_REQUEST_TIME
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _LAST_REQUEST_TIME = time.time()


async def fetch_cmc_batch(names: list[str]) -> dict[str, float]:
    """批量查询 Scryfall 获取 CMC（带缓存和限流）"""
    _clean_expired_cache()

    results = {}
    to_fetch = []

    for name in names:
        key = name.lower()
        if key in _cmc_cache:
            results[key] = _cmc_cache[key][0]
        else:
            to_fetch.append(name)

    if not to_fetch:
        return results

    chunk_size = 75
    for i in range(0, len(to_fetch), chunk_size):
        chunk = to_fetch[i:i + chunk_size]
        identifiers = [{"name": n} for n in chunk]
        try:
            _rate_limit()
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.scryfall.com/cards/collection",
                    json={"identifiers": identifiers}
                )
                data = resp.json()
                if data.get("data"):
                    now = time.time()
                    for card in data["data"]:
                        key = card.get("name", "").lower()
                        cmc = card.get("cmc") or 0
                        results[key] = cmc
                        _cmc_cache[key] = (cmc, now)
        except Exception as e:
            print(f"Scryfall batch query failed: {e}")
    return results


async def translate_name_to_en(cn_name: str) -> str:
    """使用 MTGCH API 将中文卡名翻译为英文"""
    try:
        from services.mtgch_api import MTGCHAPIClient
        client = MTGCHAPIClient(timeout=10)
        result = client.autocomplete(cn_name, size=1)
        client.close()
        if result.get("items"):
            item = result["items"][0]
            # 优先使用 name_en，否则使用 name
            return item.get("name_en") or item.get("name") or cn_name
    except Exception as e:
        print(f"MTGCH translate failed for {cn_name}: {e}")
    return cn_name


@app.post("/api/deck/cmc")
async def calc_deck_cmc(request: Request):
    """
    计算套牌 AVG CMC

    Body: {"cards": [{"name": "Lightning Bolt", "count": 4}, ...]}
    Returns: {"avgCMC": "3.24", "cmcMap": {"lightning bolt": 1.0, ...}}
    """
    body = await request.json()
    cards = body.get("cards", [])
    if not cards:
        return {"avgCMC": "0.00", "cmcMap": {}}

    # 翻译中文卡名为英文
    names = []
    for c in cards:
        name = c["name"]
        # 简单的中文检测 (Unicode 范围)
        if any('\u4e00' <= ch <= '\u9fff' for ch in name):
            # 使用 MTGCH API 翻译
            en_name = await translate_name_to_en(name)
            names.append(en_name)
        else:
            names.append(name)

    cmc_map = await fetch_cmc_batch(names)

    total_cmc = 0.0
    total_cards = 0
    for i, card in enumerate(cards):
        name = names[i]
        mv = cmc_map.get(name.lower(), 0)
        total_cmc += mv * card["count"]
        total_cards += card["count"]

    avg_cmc = f"{total_cmc / total_cards:.2f}" if total_cards > 0 else "0.00"
    return {"avgCMC": avg_cmc, "cmcMap": cmc_map}


@app.get("/api/deck/parse-url")
async def parse_deck_url(request: Request):
    """
    从 MTGGoldfish 或 Moxfield URL 解析套牌

    Query: url=https://www.mtggoldfish.com/deck/xxx
    Returns: {"success": true, "name": "Deck Name", "cards": [{"name": "Card", "count": 4}, ...]}
    """
    url = request.query_params.get("url", "")
    if not url:
        return {"success": False, "error": "缺少 URL 参数"}

    try:
        if "mtggoldfish" in url.lower():
            return parse_mtggoldfish(url)
        elif "moxfield" in url.lower():
            return parse_moxfield(url)
        else:
            return {"success": False, "error": "暂不支持该 URL 类型"}
    except Exception as e:
        return {"success": False, "error": f"解析失败: {str(e)}"}


def parse_mtggoldfish(url: str):
    """解析 MTGGoldfish 页面"""
    import html as html_module  # 用标准库解码 HTML 实体

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # 从页面提取套牌名称
    name_match = re.search(r'<h1[^>]*class="deck-view-title"[^>]*>([^<]+)', html)
    name = name_match.group(1).strip() if name_match else ""

    # 提取 Format（赛制）
    format_match = re.search(r'Format:\s*(\w+)', html)
    mtg_format = format_match.group(1).strip() if format_match else ''
    # 映射到中文赛制名称
    format_map = {
        'Standard': '标准',
        'Modern': '摩登',
        'Legacy': 'Legacy',
        'Vintage': 'Vintage',
        'Pauper': 'Pauper',
        'Commander': '指挥官',
        'Pioneer': '先驱',
        'Historic': 'Historic',
        'Explorer': 'Explorer',
        'Gladiator': 'Gladiator',
    }
    format = format_map.get(mtg_format, mtg_format or '标准')

    # MTGGoldfish 把套牌藏在隐藏字段 deck_input[deck] 里
    # 格式: "2 CardName\n4 CardName\n--\n2 SideboardCard"
    deck_input_match = re.search(r'name="deck_input\[deck\]"[^>]*value="([^"]+)"', html)
    if not deck_input_match:
        return {"success": False, "error": "未能解析到套牌数据"}

    deck_text = deck_input_match.group(1)
    # 解码 HTML 实体 (&#39; -> ', &amp; -> &, etc.)
    deck_text = html_module.unescape(deck_text)

    cards = []
    seen = {}
    current_section = "main"

    for line in deck_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line == '--':
            current_section = "sideboard"
            continue
        if current_section == "sideboard":
            # 备牌暂不处理（可扩展）
            continue
        # 解析格式: "4 CardName" 或 "4x CardName"
        match = re.match(r'^(\d+)[xX]?\s+(.+)$', line)
        if match:
            qty = int(match.group(1))
            card_name = match.group(2).strip()
            if card_name and qty > 0:
                key = card_name.lower()
                if key not in seen:
                    seen[key] = True
                    cards.append({"name": card_name, "count": qty})

    if not cards:
        return {"success": False, "error": "未能解析到套牌列表"}

    return {"success": True, "name": name, "cards": cards, "format": format}


def parse_moxfield(url: str) -> dict:
    """解析 Moxfield 页面"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # 从页面提取标题
    name_match = re.search(r'<h2[^>]*class="deck-view-info-name"[^>]*>([^<]+)', html)
    name = name_match.group(1).strip() if name_match else ""

    # Moxfield 格式: <span class="card-view-quantity">4</span>...<span class="card-view-name">Card Name</span>
    cards = []
    seen = {}
    card_matches = re.findall(r'card-view-quantity">(\d+)</span>.*?card-view-name">([^<]+)', html, re.DOTALL)
    for qty, card_name in card_matches:
        card_name = card_name.strip()
        if card_name:
            key = card_name.lower()
            if key not in seen:
                seen[key] = True
                cards.append({"name": card_name, "count": int(qty)})

    if not cards:
        return {"success": False, "error": "未能解析到套牌列表"}

    return {"success": True, "name": "Moxfield Deck", "cards": cards}


# ==================== 套牌管理 API ====================

@app.get("/api/deck/list")
async def get_deck_list(request: Request):
    """
    获取用户套牌列表

    Query参数:
    - openid (必填): 用户 openid

    返回: {"success": True, "decks": [...]}
    """
    openid = request.query_params.get("openid")
    if not openid:
        return {"success": False, "error": "openid 参数必填"}

    try:
        decks = db.get_decks_by_openid(openid)
        return {"success": True, "decks": decks}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/deck/add")
async def add_deck(request: Request):
    """
    添加套牌

    Body:
    - openid (必填): 用户 openid
    - name (必填): 套牌名称
    - format: 赛制
    - commander: 指挥官
    - cards: 卡牌列表 [{"name": "xxx", "count": 4}, ...]
    - totalCards: 总张数
    - avgCMC: 平均CMC

    返回: {"success": True, "deck": {...}}
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "请求体必须是有效 JSON"}

    openid = body.get("openid")
    name = body.get("name")
    if not openid or not name:
        return {"success": False, "error": "openid 和 name 参数必填"}

    try:
        deck_id = db.add_deck(
            openid=openid,
            name=name,
            format=body.get("format", "其他"),
            commander=body.get("commander", ""),
            cards=body.get("cards", []),
            total_cards=body.get("totalCards", 0),
            avg_cmc=body.get("avgCMC", "0.00")
        )
        return {"success": True, "deck_id": deck_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/deck/{deck_id}")
async def delete_deck(deck_id: str, request: Request):
    """
    删除套牌

    Path参数:
    - deck_id: 套牌 ID

    Query参数:
    - openid (必填): 用户 openid (用于验证所有权)

    返回: {"success": True}
    """
    openid = request.query_params.get("openid")
    if not openid:
        return {"success": False, "error": "openid 参数必填"}

    try:
        success = db.delete_deck(deck_id, openid)
        if success:
            return {"success": True}
        else:
            return {"success": False, "error": "删除失败或无权限"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/api/deck/{deck_id}")
async def update_deck(deck_id: str, request: Request):
    """
    更新套牌

    Path参数:
    - deck_id: 套牌 ID

    Body:
    - openid (必填): 用户 openid (用于验证所有权)
    - name: 套牌名称
    - format: 赛制
    - commander: 指挥官
    - cards: 卡牌列表
    - totalCards: 总张数
    - avgCMC: 平均CMC

    返回: {"success": True}
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "error": "请求体必须是有效 JSON"}

    openid = body.get("openid")
    if not openid:
        return {"success": False, "error": "openid 参数必填"}

    try:
        success = db.update_deck(
            deck_id=deck_id,
            openid=openid,
            name=body.get("name"),
            format=body.get("format"),
            commander=body.get("commander"),
            cards=body.get("cards"),
            total_cards=body.get("totalCards"),
            avg_cmc=body.get("avgCMC")
        )
        if success:
            return {"success": True}
        else:
            return {"success": False, "error": "更新失败或无权限"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_PORT, port=Config.API_PORT)
