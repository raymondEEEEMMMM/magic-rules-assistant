import os
import logging
from datetime import datetime
import uvicorn
from routes import app
from config import Config


def setup_logging():
    """配置日志系统，创建日志文件夹和日志文件"""
    # 确保日志目录存在
    log_dir = Config.LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"📁 已创建日志目录: {log_dir}")

    # 日志文件路径
    log_file = os.path.join(log_dir, Config.LOG_FILE)

    # 配置 logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    print(f"📝 日志文件: {log_file}")
    return logging.getLogger(__name__)


if __name__ == "__main__":
    logger = setup_logging()

    print("🚀 万智牌规则问答服务启动中...")
    print(f"📡 服务地址: http://{Config.API_HOST}:{Config.API_PORT}")
    print(f"📖 规则数据库: {Config.DATABASE_PATH}")
    print("\n可用端点:")
    print("  - GET  /                    服务状态")
    print("  - GET  /wechat              微信服务器验证")
    print("  - POST /wechat              微信消息接收")
    print("  - GET  /api/search?q=       规则搜索")
    print("  - GET  /api/keyword?k=      关键词异能查询")
    print("  - GET  /api/card?n=          卡牌规则查询")
    print("\n按 Ctrl+C 停止服务\n")

    logger.info(f"服务启动 - 监听 {Config.API_HOST}:{Config.API_PORT}")

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level="info"
    )
