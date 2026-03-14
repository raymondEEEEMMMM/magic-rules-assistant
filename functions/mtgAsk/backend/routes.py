from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import XMLResponse
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
