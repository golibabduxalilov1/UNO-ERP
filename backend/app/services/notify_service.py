import httpx
from app.config import settings


async def send_telegram_message(telegram_id: int, text: str):
    if not settings.BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json={"chat_id": telegram_id, "text": text, "parse_mode": "HTML"})
    except Exception:
        pass
