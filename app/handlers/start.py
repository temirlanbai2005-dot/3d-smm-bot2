from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()


def get_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔥 Сканер трендов"),
                KeyboardButton(text="✍️ Копирайтер")
            ],
            [
                KeyboardButton(text="🔎 Анализ конкурентов"),
                KeyboardButton(text="🔔 Уведомления")
            ],
        ],
        resize_keyboard=True
    )


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🎨 <b>3D SMM Assistant</b>\n\n"
        "Я помогу тебе с контентом для соцсетей!\n\n"
        "<b>Выбери функцию:</b>\n\n"
        "🔥 <b>Сканер трендов</b> - актуальные темы\n"
        "✍️ <b>Копирайтер</b> - улучшение текстов\n"
        "🔎 <b>Анализ конкурентов</b> - изучение стратегий\n"
        "🔔 <b>Уведомления</b> - ежедневные советы",
        parse_mode="HTML",
        reply_markup=get_keyboard()
    )
