from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.claude_api import claude_api
from app.utils.scraping import competitor_scraper
from app.utils.formatter import format_competitor_response, truncate_text

router = Router()


class CompetitorStates(StatesGroup):
    """Состояния для анализа конкурентов"""
    waiting_for_username = State()


@router.message(F.text == "🔎 Анализ конкурентов")
async def start_competitor_analysis(message: Message, state: FSMContext):
    """Запуск режима анализа конкурентов"""
    
    await state.set_state(CompetitorStates.waiting_for_username)
    
    await message.answer(
        "🔎 <b>АНАЛИЗ КОНКУРЕНТОВ</b>\n\n"
        "Отправьте никнейм или ссылку на профиль 3D-художника:\n\n"
        "Примеры:\n"
        "• @username\n"
        "• username\n"
        "• https://twitter.com/username\n\n"
        "Я проанализирую:\n"
        "• Частоту постов\n"
        "• Самые успешные публикации\n"
        "• Используемые форматы\n"
        "• Нишевые тренды\n\n"
        "📝 <i>Отправьте никнейм...</i>",
        parse_mode="HTML"
    )


@router.message(CompetitorStates.waiting_for_username)
async def process_competitor_analysis(message: Message, state: FSMContext):
    """Обработка анализа конкурента"""
    
    username = message.text.strip()
    
    # Очистка username от лишних символов
    username = username.replace("@", "").replace("https://", "").replace("http://", "")
    username = username.split("/")[-1]  # Берем последнюю часть URL
    
    if len(username) < 2:
        await message.answer("❌ Некорректный никнейм. Попробуйте еще раз.")
        return
    
    # Уведомление о начале
    processing_msg = await message.answer(
        f"🔎 <b>Анализирую @{username}...</b>\n\n"
        "⏳ Собираю данные профиля...",
        parse_mode="HTML"
    )
    
    try:
        # Шаг 1: Собираем данные о конкуренте
        competitor_data = await competitor_scraper.analyze_username(username)
        
        # Обновляем статус
        await processing_msg.edit_text(
            f"🔎 <b>Анализирую @{username}...</b>\n\n"
            "✅ Данные собраны\n"
            "⏳ Анализирую через Claude AI...",
            parse_mode="HTML"
        )
        
        # Шаг 2: Отправляем в Claude для анализа
        claude_response = await claude_api.analyze_competitor(competitor_data)
        
        # Шаг 3: Форматируем и отправляем
        formatted_response = format_competitor_response(claude_response)
        final_text = truncate_text(formatted_response)
        
        # Удаляем сообщение о процессе
        await processing_msg.delete()
        
        # Отправляем результат
        await message.answer(final_text, parse_mode="HTML")
        
        # Сбрасываем состояние
        await state.clear()
        
        # Дополнительная подсказка
        await message.answer(
            "💡 <b>Применяйте инсайты в своей стратегии!</b>\n\n"
            "Хотите проанализировать еще одного конкурента?\n"
            "Нажмите 🔎 Анализ конкурентов снова.",
            parse_mode="HTML"
        )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ <b>Ошибка при анализе</b>\n\n"
            f"Попробуйте другой никнейм или повторите позже.",
            parse_mode="HTML"
        )
        await state.clear()
