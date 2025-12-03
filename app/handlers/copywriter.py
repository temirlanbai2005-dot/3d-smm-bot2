from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.claude_api import claude_api
from app.utils.formatter import format_copy_response, truncate_text

router = Router()


class CopywriterStates(StatesGroup):
    """Состояния для копирайтера"""
    waiting_for_text = State()


@router.message(F.text == "✍️ Копирайтер")
async def start_copywriter(message: Message, state: FSMContext):
    """Запуск режима копирайтера"""
    
    await state.set_state(CopywriterStates.waiting_for_text)
    
    await message.answer(
        "✍️ <b>РЕЖИМ КОПИРАЙТЕРА</b>\n\n"
        "Отправьте мне текст, который нужно переписать.\n\n"
        "Я верну вам:\n"
        "• Исправленную версию\n"
        "• Короткую версию\n"
        "• Развернутую версию\n"
        "• Эмоциональную версию\n"
        "• Версию для Twitter\n"
        "• Версию для Threads\n"
        "• Версию для LinkedIn\n\n"
        "📝 <i>Просто отправьте текст...</i>",
        parse_mode="HTML"
    )


@router.message(CopywriterStates.waiting_for_text)
async def process_copywriting(message: Message, state: FSMContext):
    """Обработка текста через Claude"""
    
    user_text = message.text
    
    # Проверка длины
    if len(user_text) < 10:
        await message.answer(
            "❌ Текст слишком короткий. Отправьте хотя бы несколько предложений."
        )
        return
    
    if len(user_text) > 2000:
        await message.answer(
            "❌ Текст слишком длинный. Максимум 2000 символов."
        )
        return
    
    # Уведомление о начале обработки
    processing_msg = await message.answer(
        "✍️ <b>Обрабатываю текст...</b>\n\n"
        "⏳ Claude AI создает варианты...",
        parse_mode="HTML"
    )
    
    try:
        # Отправляем в Claude
        claude_response = await claude_api.rewrite_copy(user_text)
        
        # Форматируем результат
        formatted_response = format_copy_response(claude_response)
        final_text = truncate_text(formatted_response)
        
        # Удаляем сообщение о процессе
        await processing_msg.delete()
        
        # Отправляем результат
        await message.answer(final_text, parse_mode="HTML")
        
        # Сбрасываем состояние
        await state.clear()
        
        # Предлагаем дальнейшие действия
        await message.answer(
            "💡 <b>Хотите переписать еще один текст?</b>\n"
            "Нажмите ✍️ Копирайтер снова или выберите другую функцию.",
            parse_mode="HTML"
        )
    
    except Exception as e:
        await processing_msg.edit_text(
            "❌ <b>Ошибка при обработке текста</b>\n\n"
            "Попробуйте еще раз или нажмите /start",
            parse_mode="HTML"
        )
        await state.clear()
