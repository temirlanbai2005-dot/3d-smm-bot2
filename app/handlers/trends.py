from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.claude_api import claude_api
from app.utils.scraping import trend_scraper
from app.utils.formatter import format_trend_response, truncate_text

router = Router()


@router.message(F.text == "🔥 Сканер трендов")
async def handle_trends(message: Message, state: FSMContext):
    """Обработчик сканера трендов"""
    
    await state.clear()
    
    # Отправляем уведомление о начале работы
    processing_msg = await message.answer(
        "🔍 <b>Сканирую тренды...</b>\n\n"
        "⏳ Собираю данные из Reddit, YouTube и других источников...",
        parse_mode="HTML"
    )
    
    try:
        # Шаг 1: Собираем тренды
        raw_trends = await trend_scraper.get_all_trends()
        
        # Обновляем статус
        await processing_msg.edit_text(
            "🔍 <b>Сканирую тренды...</b>\n\n"
            "✅ Данные собраны\n"
            "⏳ Анализирую через Claude AI...",
            parse_mode="HTML"
        )
        
        # Шаг 2: Отправляем в Claude для анализа
        claude_response = await claude_api.analyze_trends(raw_trends)
        
        # Шаг 3: Форматируем и отправляем результат
        formatted_response = format_trend_response(claude_response)
        final_text = truncate_text(formatted_response)
        
        # Удаляем сообщение о процессе
        await processing_msg.delete()
        
        # Отправляем результат
        await message.answer(final_text, parse_mode="HTML")
        
        # Отправляем дополнительную подсказку
        await message.answer(
            "💡 <b>Что делать дальше?</b>\n\n"
            "• Используйте идеи для создания контента\n"
            "• Отправьте текст в ✍️ Копирайтер для улучшения\n"
            "• Изучите конкурентов через 🔎 Анализ конкурентов",
            parse_mode="HTML"
        )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ <b>Ошибка при анализе трендов</b>\n\n"
            f"Попробуйте еще раз через минуту.\n"
            f"Если проблема повторяется, нажмите /start",
            parse_mode="HTML"
        )
