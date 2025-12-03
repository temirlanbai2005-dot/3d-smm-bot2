import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)


class NotificationScheduler:
    def __init__(self, tz: str):
        try:
            timezone = pytz.timezone(tz)
        except:
            timezone = pytz.UTC
        
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        self.is_running = False
    
    def add_daily_job(self, callback, time_str: str):
        try:
            hour, minute = map(int, time_str.split(":"))
            trigger = CronTrigger(hour=hour, minute=minute)
            self.scheduler.add_job(
                callback, 
                trigger=trigger, 
                id="daily_notification", 
                replace_existing=True
            )
            logger.info(f"Scheduled daily job at {time_str}")
        except Exception as e:
            logger.error(f"Failed to schedule job: {e}")
    
    def start(self):
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started")
    
    def shutdown(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")


from app.config import settings
scheduler = NotificationScheduler(settings.TIMEZONE)
