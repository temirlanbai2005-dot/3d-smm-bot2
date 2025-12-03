from aiogram import Router, F, Bot
from aiogram.types import Message
import json
import os
import logging
from app.claude_api import claude_api

router = Router()
logger = logging.getLogger(__name__)

SUBS_FILE = "subscribers.json"


def load_subscribers():
    if os.path.exists(SUBS_FILE):
        try:
            with open(SUBS_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()


def save_subscribers(subs):
    try:
        with open(SUBS_FILE, "w") as f:
            json.dump(list(subs), f)
    except Exception as e:
        logger.error(f"Error saving subscribers: {e}")


@router.message(F.text == "🔔 Уведомления")
async def toggle_notifications(message: Message):
    subs = load_subscribers()
    user_id = message.from_user.id
    
    if user_id in subs:
        subs.remove(user_id)
        save_subscribers(subs)
        await message.answer(
            "🔕 <b>Уведомления отключены</b>\n\n"
            "Вы больше не будете получать ежедневные советы.",
            parse_mode="HTML"
        )
    else:
        subs.add(user_id)
        save_subscribers(subs)
        await message.answer(
            "🔔 <b>Уведомления включены!</b>\n\n"
            "Каждое утро в 09:00 (МСК) вы будете получать:\n"
            "💡 Идею дня\n"
            "🎨 Совет дня\n"
            "⏰ Лучшее время для постинга\n"
            "🔥 Актуальные тренды",
            parse_mode="HTML"
        )


async def send_daily_notifications(bot: Bot):
    """Отправка ежедневных уведомлений"""
    subs = load_subscribers()
    
    if not subs:
        logger.info("No subscribers")
        return
    
    logger.info(f"Sending to {len(subs)} users")
    
    try:
        content = await claude_api.generate_daily_content()
        
        if content:
            for user_id in list(subs):
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"🌅 <b>ДОБРОЕ УТРО, 3D-ХУДОЖНИК!</b>\n\n{content}",
                        parse_mode="HTML"
                    )
                    logger.info(f"Sent to {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send to {user_id}: {e}")
                    if "bot was blocked" in str(e).lower():
                        subs.discard(user_id)
            
            save_subscribers(subs)
    
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        logger.info("Daily notifications completed")
    
    except Exception as e:
        logger.error(f"Error generating daily content: {e}")
