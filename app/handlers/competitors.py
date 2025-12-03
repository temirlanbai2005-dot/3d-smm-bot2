from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.claude_api import claude_api
from app.utils.scraping import competitor_scraper

router = Router()


class CompetitorStates(StatesGroup):
    waiting_for_username = State()


@router.message(F.text == "🔎 Анализ конкурентов")
async def start_competitor_analysis(message: Message, state: FSMContext):
    await state.set_state(CompetitorStates.waiting_for_username)
    await message.answer(
        "🔎 <b>АНАЛИЗ КОНКУРЕНТОВ</b>\n\n"
        "Отправь никнейм или ссылку на профиль 3D-художника:\n\n"
        "Примеры:\n"
        "• @username\n"
        "• username\n"
        "• https://twitter.com/username\n\n"
        "📝 Жду никнейм...",
        parse_mode="HTML"
    )


@router.message(CompetitorStates.waiting_for_username)
async def process_competitor(message: Message, state: FSMContext):
    username = message.text.strip().replace("@", "").replace("https://", "").replace("http://", "")
    username = username.split("/")[-1]
    
    if len(username) < 2:
        await message.answer("❌ Некорректный никнейм. Попробуйте еще раз.")
        return
    
    msg = await message.answer(f"🔎 <b>Анализирую @{username}...</b>\n⏳ Собираю данные...", parse_mode="HTML")
    
    try:
        # Собираем данные
        data = await competitor_scraper.analyze_username(username)
        
        await msg.edit_text(f"🔎 <b>Анализирую @{username}...</b>\n✅ Данные собраны\n⏳ Анализирую...", parse_mode="HTML")
        
        # Анализируем через Claude
        response = await claude_api.analyze_competitor(data)
        
        await msg.delete()
        await state.clear()
        
        if response:
            if len(response) > 4000:
                response = response[:3900] + "\n\n... (обрезано)"
            
            await message.answer(f"🔎 <b>АНАЛИЗ КОНКУРЕНТА</b>\n\n{response}", parse_mode="HTML")
        else:
            await message.answer("❌ Ошибка при анализе. Попробуйте позже.")
    
    except Exception as e:
        await msg.delete()
        await state.clear()
        await message.answer("❌ Произошла ошибка. Попробуйте снова.")
