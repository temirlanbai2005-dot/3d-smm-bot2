import os
from typing import Optional


class Settings:
    """Настройки приложения из переменных окружения"""
    
    def __init__(self):
        # Telegram
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
        self.PORT = int(os.getenv("PORT", 10000))
        
        # Claude API
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        self.CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
        self.CLAUDE_MAX_TOKENS = 4000
        
        # Notifications
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
        self.NOTIFICATION_TIME = os.getenv("NOTIFICATION_TIME", "09:00")
        self.NOTIFICATION_USERS = os.getenv("NOTIFICATION_USERS")


settings = Settings()
