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

    # OpenCLAW Gateway 配置（自建服务器）
    OPENCLAW_ENABLED = os.getenv("OPENCLAW_ENABLED", "true").lower() == "true"
    OPENCLAW_HOST = os.getenv("OPENCLAW_HOST", "101.43.48.45")  # 自建服务器 IP
    OPENCLAW_PORT = os.getenv("OPENCLAW_PORT", "19601")
    OPENCLAW_SSH_USER = os.getenv("OPENCLAW_SSH_USER", "openclaw")  # 专用用户，非 root
    OPENCLAW_SSH_PASSWORD = os.getenv("OPENCLAW_SSH_PASSWORD", "")  # SSH 密码
    OPENCLAW_SSH_KEY = os.getenv("OPENCLAW_SSH_KEY", "")  # SSH 密钥路径（绝对路径）
    OPENCLAW_SSH_KEY_CONTENT = os.getenv("OPENCLAW_SSH_KEY_CONTENT", "")  # SSH 私钥内容（Base64 编码）
    OPENCLAW_AGENT = os.getenv("OPENCLAW_AGENT", "main")  # Agent 名称

    # Agent 池配置
    OPENCLAW_MAX_AGENTS = int(os.getenv("OPENCLAW_MAX_AGENTS", "100"))  # 最大 Agent 数量
    OPENCLAW_IDLE_TIMEOUT = int(os.getenv("OPENCLAW_IDLE_TIMEOUT", "30"))  # 空闲超时（分钟）

    # Mock 模式配置（用于测试，不消耗 token）
    OPENCLAW_MOCK = os.getenv("OPENCLAW_MOCK", "false").lower() == "true"

    # 数据库配置
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/magic_rules.db")

    # API配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # 日志配置
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    LOG_FILE = os.getenv("LOG_FILE", f"mtgask_{datetime.now().strftime('%Y%m%d')}.log")

config = Config()
