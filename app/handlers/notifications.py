from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
import json
import os
from app.claude_api import claude_api
from app.utils.formatter import format_daily_notification
from app.utils.scheduler import scheduler
import logging

router = Router()
logger = logging.getLogger(__name__)

# Файл для хранения подписчиков
SUBSCRIBERS_FILE = "subscribers.json"


class NotificationCallback(CallbackData, prefix="notif"):
    """Callback для кнопок уведомлений"""
    action: str  # "enable" или "disable"


def load_subscribers() -> set:
    """Загрузка списка подписчиков из файла"""
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, "r") as f:
                data = json.load(f)
                return set(data)
        except Exception as e:
            logger.error(f"Error loading subscribers: {e}")
    return set()


def save_subscribers(subscribers: set):
    """Сохранение списка подписчиков в файл"""
    try:
        with open(SUBSCRIBERS_FILE, "w") as f:
            json.dump(list(subscribers), f)
    except Exception as e:
        logger.error(f"Error saving subscribers: {e}")


def get_notification_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для управления уведомлениями"""
    subscribers = load_subscribers()
    is_subscribed = user_id in subscribers
    
    if is_subscribed:
        button = InlineKeyboardButton(
            text="🔕 Отключить уведомления",
            callback_data=NotificationCallback(action="disable").pack()
        )
    else:
        button = InlineKeyboardButton(
            text="🔔 Включить уведомления",
            callback_data=NotificationCallback(action="enable").pack()
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard


@router.message(F.text == "🔔 Настройки уведомлений")
async def notification_settings(message: Message):
    """Настройки уведомлений"""
    
    subscribers = load_subscribers()
    is_subscribed = message.from_user.id in subscribers
    
    if is_subscribed:
        status = "✅ <b>Уведомления включены</b>"
    else:
        status = "🔕 <b>Уведомления отключены</b>"
    
    text = f"""
🔔 <b>ЕЖЕДНЕВНЫЕ УВЕДОМЛЕНИЯ</b>

{status}

<b>Что вы получаете каждое утро:</b>
💡 Идея дня для 3D-проекта
🎨 Совет дня по 3D или SMM
⏰ Лучшее время для постинга
🔥 Актуальные тренды

<b>Время отправки:</b> 09:00 (МСК)

Используйте кнопку ниже для управления подпиской:
    """
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_notification_keyboard(message.from_user.id)
    )


@router.callback_query(NotificationCallback.filter())
async def toggle_notifications(callback: CallbackQuery, callback_data: NotificationCallback):
    """Переключение уведомлений"""
    
    user_id = callback.from_user.id
    subscribers = load_subscribers()
    
    if callback_data.action == "enable":
        subscribers.add(user_id)
        save_subscribers(subscribers)
        status = "✅ <b>Уведомления включены!</b>"
        message = "Вы будете получать ежедневные советы каждое утро в 09:00 (МСК)"
    
    else:  # disable
        if user_id in subscribers:
            subscribers.remove(user_id)
            save_subscribers(subscribers)
        status = "🔕 <b>Уведомления отключены</b>"
        message = "Вы больше не будете получать ежедневные уведомления"
    
    text = f"""
🔔 <b>ЕЖЕДНЕВНЫЕ УВЕДОМЛЕНИЯ</b>

{status}

{message}

<b>Что включают уведомления:</b>
💡 Идея дня для 3D-проекта
🎨 Совет дня по 3D или SMM
⏰ Лучшее время для постинга
🔥 Актуальные тренды
    """
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_notification_keyboard(user_id)
    )
    
    await callback.answer()


async def send_daily_notifications(bot: Bot):
    """
    Функция для отправки ежедневных уведомлений
    Вызывается по расписанию
    """
    subscribers = load_subscribers()
    
    if not subscribers:
        logger.info("No subscribers for daily notifications")
        return
    
    logger.info(f"Sending daily notifications to {len(subscribers)} users")
    
    # Генерируем контент
    try:
        daily_content = await claude_api.generate_daily_content()
        formatted_content = format_daily_notification(daily_content)
        
        # Отправляем всем подписчикам
        for user_id in subscribers:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=formatted_content,
                    parse_mode="HTML"
                )
                logger.info(f"Notification sent to {user_id}")
            
            except Exception as e:
                logger.error(f"Failed to send notification to {user_id}: {e}")
                # Если пользователь заблокировал бота, удаляем его из подписчиков
                if "bot was blocked" in str(e).lower():
                    subscribers.discard(user_id)
        
        # Сохраняем обновленный список подписчиков
        save_subscribers(subscribers)
        
        logger.info("Daily notifications completed")
    
    except Exception as e:
        logger.error(f"Error generating daily content: {e}")
