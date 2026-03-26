from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import XMLResponse, StreamingResponse
from typing import Optional
import hashlib
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

@app.get("/wechat")
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
async def get_card_rule(card_name: str):
    """获取卡牌规则API"""
    result = rule_service.get_card_rule(card_name)
    if result:
        return {"card_name": card_name, "result": result}
    return {"card_name": card_name, "result": None}

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
    from services.ai_judge_service import ai_judge_service
    ai_judge_service.clear_session(session_id)
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

    from services.ai_judge_service import ai_judge_service
    ai_judge_service.clear_session(session_id)
    return {"success": True, "message": "会话已清除"}


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


# ==================== 反馈 API ====================

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
