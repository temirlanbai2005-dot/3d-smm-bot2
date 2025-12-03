from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBHOOK_PATH: str = "/webhook"
    PORT: int = 8000
    
    # Claude API
    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS: int = 4000
    
    # Notifications
    TIMEZONE: str = "Europe/Moscow"
    NOTIFICATION_TIME: str = "09:00"
    NOTIFICATION_USERS: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
