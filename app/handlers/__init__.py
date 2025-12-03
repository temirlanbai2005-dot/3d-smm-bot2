from aiogram import Router
from app.handlers import start, trends, copywriter, competitors, notifications

# Главный роутер для всех хэндлеров
main_router = Router()

# Подключаем все роутеры
main_router.include_router(start.router)
main_router.include_router(trends.router)
main_router.include_router(copywriter.router)
main_router.include_router(competitors.router)
main_router.include_router(notifications.router)
