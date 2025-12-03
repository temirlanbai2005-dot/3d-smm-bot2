import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from app.config import settings
from app.handlers import start, trends, copywriter, competitors, notifications
from app.utils.scheduler import scheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(trends.router)
dp.include_router(copywriter.router)
dp.include_router(competitors.router)
dp.include_router(notifications.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    logger.info("Starting bot...")
    
    # Устанавливаем webhook
    webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    logger.info(f"Webhook set: {webhook_url}")
    
    # Запускаем планировщик
    async def daily_job():
        await notifications.send_daily_notifications(bot)
    
    scheduler.add_daily_job(daily_job, settings.NOTIFICATION_TIME)
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await bot.delete_webhook()
    scheduler.shutdown()
    await bot.session.close()
    logger.info("Bot stopped")


app = FastAPI(lifespan=lifespan)


@app.post(settings.WEBHOOK_PATH)
async def webhook_handler(request: Request):
    try:
        update = Update(**await request.json())
        await dp.feed_update(bot, update)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=500)


@app.get("/")
async def root():
    return {
        "status": "running",
        "bot": "3D SMM Assistant",
        "version": "1.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
