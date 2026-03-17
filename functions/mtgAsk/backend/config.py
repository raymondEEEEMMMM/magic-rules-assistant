import os
from datetime import datetime

class Config:
    # 微信公众号配置
    WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
    WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")
    WECHAT_ENCODING_AES_KEY = os.getenv("WECHAT_ENCODING_AES_KEY", "")

    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # MiniMax配置
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

    # 数据库配置
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/magic_rules.db")

    # API配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # 日志配置
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    LOG_FILE = os.getenv("LOG_FILE", f"mtgask_{datetime.now().strftime('%Y%m%d')}.log")

config = Config()
