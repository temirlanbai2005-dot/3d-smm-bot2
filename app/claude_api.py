import aiohttp
import asyncio
import logging
from typing import Optional, List, Dict
from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeAPI:
    """Обертка для работы с Claude API"""
    
    BASE_URL = "https://api.anthropic.com/v1/messages"
    
    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def send_message(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Отправка запроса к Claude API с retry логикой
        
        Args:
            prompt: Основной промпт
            system_prompt: Системный промпт (опционально)
            temperature: Температура генерации (0-1)
            max_retries: Количество повторных попыток при ошибке
        
        Returns:
            Ответ от Claude или None при ошибке
        """
        
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.BASE_URL,
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            return data["content"][0]["text"]
                        
                        elif response.status == 429:
                            # Rate limit - ждем и повторяем
                            wait_time = 2 ** attempt
                            logger.warning(f"Rate limit hit. Waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        
                        else:
                            error_text = await response.text()
                            logger.error(f"Claude API error {response.status}: {error_text}")
                            
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            
                            return None
            
            except asyncio.TimeoutError:
                logger.error(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                return None
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                return None
        
        return None
    
    async def analyze_trends(self, raw_data: str) -> Optional[str]:
        """Анализ трендов для 3D-художника"""
        
        system_prompt = """Ты эксперт по SMM и 3D-графике. Твоя задача — анализировать тренды 
        и давать конкретные рекомендации для 3D-художников."""
        
        prompt = f"""Проанализируй следующие тренды и создай отчет для 3D-художника:

{raw_data}

Верни результат в следующем формате:

📊 ТОП-5 ТРЕНДОВ:
1. [Название тренда]
2. [Название тренда]
3. [Название тренда]
4. [Название тренда]
5. [Название тренда]

💡 КАК АДАПТИРОВАТЬ ДЛЯ 3D:
[Конкретные идеи для каждого тренда]

📝 ПРИМЕРЫ ПОСТОВ:

🐦 Twitter:
[Короткий пост 1-2 предложения]

🧵 Threads:
[Пост для Threads]

💼 LinkedIn:
[Профессиональный пост]

Будь конкретным и креативным!"""
        
        return await self.send_message(prompt, system_prompt)
    
    async def rewrite_copy(self, text: str) -> Optional[str]:
        """Переписывание текста в разных форматах"""
        
        system_prompt = """Ты профессиональный копирайтер и SMM-специалист. 
        Твоя задача — улучшать тексты для социальных сетей."""
        
        prompt = f"""Перепиши следующий текст в нескольких вариантах:

ИСХОДНЫЙ ТЕКСТ:
{text}

Верни результат в формате:

✅ ИСПРАВЛЕННАЯ ВЕРСИЯ:
[Грамматически правильный текст]

📏 КОРОТКАЯ ВЕРСИЯ:
[Сжатая версия, до 280 символов]

📖 РАЗВЕРНУТАЯ ВЕРСИЯ:
[Подробная версия с деталями]

❤️ ЭМОЦИОНАЛЬНАЯ ВЕРСИЯ:
[С эмоциями и восклицаниями]

🐦 ДЛЯ TWITTER:
[Оптимизировано для Twitter]

🧵 ДЛЯ THREADS:
[Оптимизировано для Threads]

💼 ДЛЯ LINKEDIN:
[Профессиональный стиль]"""
        
        return await self.send_message(prompt, system_prompt)
    
    async def analyze_competitor(self, competitor_data: str) -> Optional[str]:
        """Анализ конкурента"""
        
        system_prompt = """Ты аналитик SMM и эксперт по контент-стратегии. 
        Анализируй конкурентов и давай практические рекомендации."""
        
        prompt = f"""Проанализируй данные конкурента (3D-художника):

{competitor_data}

Верни анализ в формате:

📊 СТАТИСТИКА:
[Частота постов, форматы контента]

🔥 САМЫЕ УСПЕШНЫЕ ПОСТЫ:
[Топ-3 с описанием]

📈 ЧТО РАБОТАЕТ:
[Паттерны успешного контента]

💡 РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ ТВОЕГО КОНТЕНТА:
[Конкретные советы]

🎯 НИШЕВЫЕ ТРЕНДЫ:
[Специфичные темы для 3D]"""
        
        return await self.send_message(prompt, system_prompt)
    
    async def generate_daily_content(self) -> Optional[str]:
        """Генерация ежедневного контента"""
        
        system_prompt = """Ты ментор для 3D-художников. Каждый день ты даешь 
        вдохновение, советы и актуальную информацию."""
        
        prompt = """Создай ежедневную рассылку для 3D-художника:

💡 ИДЕЯ ДНЯ:
[Креативная идея для 3D-проекта]

🎨 СОВЕТ ДНЯ:
[Практический совет по 3D или SMM]

⏰ ЛУЧШЕЕ ВРЕМЯ ДЛЯ ПОСТИНГА:
[Рекомендация с объяснением]

🔥 ЧТО СЕЙЧАС В ТРЕНДЕ:
[Актуальная тема в 3D/дизайне]

Будь мотивирующим и конкретным!"""
        
        return await self.send_message(prompt, system_prompt, temperature=0.8)


# Singleton экземпляр
claude_api = ClaudeAPI()
