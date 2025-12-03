from typing import Optional


def format_trend_response(claude_response: Optional[str]) -> str:
    """Форматирование ответа о трендах"""
    if not claude_response:
        return "❌ Ошибка при анализе трендов. Попробуйте позже."
    
    return f"🔥 <b>АНАЛИЗ ТРЕНДОВ ДЛЯ 3D-ХУДОЖНИКА</b>\n\n{claude_response}"


def format_copy_response(claude_response: Optional[str]) -> str:
    """Форматирование ответа копирайтера"""
    if not claude_response:
        return "❌ Ошибка при обработке текста. Попробуйте позже."
    
    return f"✍️ <b>ВАРИАНТЫ ТЕКСТА</b>\n\n{claude_response}"


def format_competitor_response(claude_response: Optional[str]) -> str:
    """Форматирование ответа анализа конкурентов"""
    if not claude_response:
        return "❌ Ошибка при анализе конкурента. Попробуйте позже."
    
    return f"🔎 <b>АНАЛИЗ КОНКУРЕНТА</b>\n\n{claude_response}"


def format_daily_notification(claude_response: Optional[str]) -> str:
    """Форматирование ежедневного уведомления"""
    if not claude_response:
        return "❌ Ошибка при генерации контента."
    
    return f"🌅 <b>ДОБРОЕ УТРО, 3D-ХУДОЖНИК!</b>\n\n{claude_response}"


def truncate_text(text: str, max_length: int = 4000) -> str:
    """
    Обрезка текста до максимальной длины (лимит Telegram)
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
    
    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 100] + "\n\n... (текст обрезан из-за лимита Telegram)"
