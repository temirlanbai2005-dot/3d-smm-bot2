from aiogram import Router, F
from aiogram.types import Message
from app.claude_api import claude_api
from app.utils.scraping import trend_scraper

router = Router()


@router.message(F.text == "🔥 Сканер трендов")
async def handle_trends(message: Message):
    msg = await message.answer("🔍 <b>Сканирую тренды...</b>\n⏳ Собираю данные...", parse_mode="HTML")
    
    try:
        # Собираем тренды
        raw_trends = await trend_scraper.get_all_trends()
        
        await msg.edit_text("🔍 <b>Сканирую тренды...</b>\n✅ Данные собраны\n⏳ Анализирую через Claude AI...", parse_mode="HTML")
        
        # Анализируем через Claude
        response = await claude_api.analyze_trends(raw_trends)
        
        await msg.delete()
        
        if response:
            # Обрезаем если слишком длинный
            if len(response) > 4000:
                response = response[:3900] + "\n\n... (обрезано)"
            
            await message.answer(f"🔥 <b>АНАЛИЗ ТРЕНДОВ</b>\n\n{response}", parse_mode="HTML")
        else:
            await message.answer("❌ Ошибка при анализе. Попробуйте позже.")
    
    except Exception as e:
        await msg.delete()
        await message.answer(f"❌ Произошла ошибка. Попробуйте снова.")
