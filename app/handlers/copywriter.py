from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.claude_api import claude_api

router = Router()


class CopyStates(StatesGroup):
    waiting_for_text = State()


@router.message(F.text == "✍️ Копирайтер")
async def start_copywriter(message: Message, state: FSMContext):
    await state.set_state(CopyStates.waiting_for_text)
    await message.answer(
        "✍️ <b>РЕЖИМ КОПИРАЙТЕРА</b>\n\n"
        "Отправь мне текст, который нужно переписать.\n\n"
        "Я верну:\n"
        "• Исправленную версию\n"
        "• Короткую версию\n"
        "• Развернутую версию\n"
        "• Эмоциональную версию\n"
        "• Версии для Twitter, Threads, LinkedIn\n\n"
        "📝 Жду текст...",
        parse_mode="HTML"
    )


@router.message(CopyStates.waiting_for_text)
async def process_copywriting(message: Message, state: FSMContext):
    text = message.text
    
    if len(text) < 10:
        await message.answer("❌ Текст слишком короткий. Минимум 10 символов.")
        return
    
    if len(text) > 2000:
        await message.answer("❌ Текст слишком длинный. Максимум 2000 символов.")
        return
    
    msg = await message.answer("✍️ <b>Обрабатываю текст...</b>\n⏳ Claude AI создает варианты...", parse_mode="HTML")
    
    try:
        response = await claude_api.rewrite_copy(text)
        
        await msg.delete()
        await state.clear()
        
        if response:
            if len(response) > 4000:
                response = response[:3900] + "\n\n... (обрезано)"
            
            await message.answer(f"✍️ <b>ВАРИАНТЫ ТЕКСТА</b>\n\n{response}", parse_mode="HTML")
        else:
            await message.answer("❌ Ошибка при обработке. Попробуйте позже.")
    
    except Exception as e:
        await msg.delete()
        await state.clear()
        await message.answer("❌ Произошла ошибка. Попробуйте снова.")
