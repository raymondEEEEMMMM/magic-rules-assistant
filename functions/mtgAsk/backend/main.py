import uvicorn
from routes import app
from config import Config

if __name__ == "__main__":
    print("MTG Rule Q&A Service Starting...")
    print(f"Server: http://{Config.API_HOST}:{Config.API_PORT}")
    print(f"Database: {Config.DATABASE_PATH}")
    print("\n可用端点:")
    print("  - GET  /                    服务状态")
    print("  - GET  /wechat              微信服务器验证")
    print("  - POST /wechat              微信消息接收")
    print("  - GET  /api/search?q=       规则搜索")
    print("  - GET  /api/keyword?k=      关键词异能查询")
    print("  - GET  /api/card?n=          卡牌规则查询")
    print("\n按 Ctrl+C 停止服务\n")

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level="info"
    )
