import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from app.config import settings
from app.handlers import main_router
from app.handlers.notifications import send_daily_notifications
from app.utils.scheduler import scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(main_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI"""
    
    # Startup
    logger.info("Starting bot...")
    
    # Устанавливаем webhook
    webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    logger.info(f"Webhook set to: {webhook_url}")
    
    # Запускаем планировщик уведомлений
    async def daily_notification_job():
        """Обертка для задачи уведомлений"""
        await send_daily_notifications(bot)
    
    scheduler.add_daily_job(daily_notification_job, settings.NOTIFICATION_TIME)
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down bot...")
    await bot.delete_webhook()
    scheduler.shutdown()
    await bot.session.close()
    logger.info("Bot stopped")


# Создаем FastAPI приложение
app = FastAPI(lifespan=lifespan)


@app.post(settings.WEBHOOK_PATH)
async def webhook_handler(request: Request) -> Response:
    """Обработчик webhook от Telegram"""
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return Response(status_code=500)


@app.get("/")
async def root():
    """Healthcheck endpoint"""
    return {
        "status": "running",
        "bot": "3D SMM Assistant",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check для мониторинга"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT
    )
