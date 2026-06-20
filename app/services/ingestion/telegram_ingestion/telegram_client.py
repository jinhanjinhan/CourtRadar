from telethon import TelegramClient, events

from app.core.config import settings

if not settings.telegram_api_id or not settings.telegram_api_hash:
    raise RuntimeError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")


client = TelegramClient(
    session="telegram_scraper_session",
    api_id=int(settings.telegram_api_id),
    api_hash=settings.telegram_api_hash,
)
