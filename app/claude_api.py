import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


class ClaudeAPI:
    BASE_URL = "https://api.anthropic.com/v1/messages"
    
    def __init__(self, api_key: str, model: str, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def send_message(self, prompt: str, system_prompt: str = None, temperature: float = 0.7):
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        for attempt in range(3):
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
                            await asyncio.sleep(2 ** attempt)
                            continue
                        else:
                            logger.error(f"Claude API error: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"Error: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                return None
        return None
    
    async def analyze_trends(self, raw_data: str):
        system = "Ты эксперт по SMM и 3D-графике. Анализируй тренды для 3D-художников."
        prompt = f"""Проанализируй тренды:

{raw_data}

Верни в формате:

📊 ТОП-5 ТРЕНДОВ:
1. [тренд]
2. [тренд]
3. [тренд]
4. [тренд]
5. [тренд]

💡 КАК АДАПТИРОВАТЬ ДЛЯ 3D:
[конкретные идеи]

📝 ПРИМЕРЫ ПОСТОВ:

🐦 Twitter:
[пост]

🧵 Threads:
[пост]

💼 LinkedIn:
[пост]"""
        
        return await self.send_message(prompt, system)
    
    async def rewrite_copy(self, text: str):
        system = "Ты профессиональный копирайтер."
        prompt = f"""Перепиши этот текст:

{text}

Верни в формате:

✅ ИСПРАВЛЕННАЯ ВЕРСИЯ:
[текст]

📏 КОРОТКАЯ ВЕРСИЯ (до 280 символов):
[текст]

📖 РАЗВЕРНУТАЯ ВЕРСИЯ:
[текст]

❤️ ЭМОЦИОНАЛЬНАЯ ВЕРСИЯ:
[текст]

🐦 ДЛЯ TWITTER:
[текст]

🧵 ДЛЯ THREADS:
[текст]

💼 ДЛЯ LINKEDIN:
[текст]"""
        
        return await self.send_message(prompt, system)
    
    async def analyze_competitor(self, data: str):
        system = "Ты аналитик SMM для 3D-художников."
        prompt = f"""Проанализируй конкурента:

{data}

Верни:

📊 СТАТИСТИКА:
[частота постов, форматы]

🔥 САМЫЕ УСПЕШНЫЕ ПОСТЫ:
[топ-3 с описанием]

📈 ЧТО РАБОТАЕТ:
[паттерны]

💡 РЕКОМЕНДАЦИИ:
[конкретные советы]

🎯 НИШЕВЫЕ ТРЕНДЫ:
[темы]"""
        
        return await self.send_message(prompt, system)
    
    async def generate_daily_content(self):
        system = "Ты ментор для 3D-художников."
        prompt = """Создай ежедневную мотивационную рассылку:

💡 ИДЕЯ ДНЯ:
[креативная идея для 3D-проекта]

🎨 СОВЕТ ДНЯ:
[практический совет]

⏰ ЛУЧШЕЕ ВРЕМЯ ДЛЯ ПОСТИНГА:
[рекомендация с объяснением]

🔥 ЧТО СЕЙЧАС В ТРЕНДЕ:
[актуальная тема в 3D/дизайне]

Будь вдохновляющим!"""
        
        return await self.send_message(prompt, system, temperature=0.8)


from app.config import settings
claude_api = ClaudeAPI(settings.CLAUDE_API_KEY, settings.CLAUDE_MODEL, settings.CLAUDE_MAX_TOKENS)


# Singleton экземпляр
claude_api = ClaudeAPI()
