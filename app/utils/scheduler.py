import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Планировщик для ежедневных уведомлений"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=timezone(settings.TIMEZONE))
        self.is_running = False
    
    def add_daily_job(self, callback, time_str: str = None):
        """
        Добавление ежедневной задачи
        
        Args:
            callback: Асинхронная функция для вызова
            time_str: Время в формате "HH:MM"
        """
        if time_str is None:
            time_str = settings.NOTIFICATION_TIME
        
        try:
            hour, minute = map(int, time_str.split(":"))
            
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=timezone(settings.TIMEZONE)
            )
            
            self.scheduler.add_job(
                callback,
                trigger=trigger,
                id="daily_notification",
                replace_existing=True
            )
            
            logger.info(f"Scheduled daily notification at {time_str} ({settings.TIMEZONE})")
        
        except Exception as e:
            logger.error(f"Failed to schedule job: {e}")
    
    def start(self):
        """Запуск планировщика"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Остановка планировщика"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")


# Singleton
scheduler = NotificationScheduler()
