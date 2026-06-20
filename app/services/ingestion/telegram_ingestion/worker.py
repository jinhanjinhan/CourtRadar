import asyncio
import logging

from telethon import events

from app.core.config import settings
from app.services.ingestion.telegram_ingestion.telegram_client import client
from app.services.ingestion.telegram_ingestion.service import TelegramIngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_source_groups() -> list[str | int]:
    groups = []

    for raw_group in settings.telegram_source_groups.split(","):
        group = raw_group.strip()

        if not group:
            continue

        if group.lstrip("-").isdigit():
            groups.append(int(group))
        else:
            groups.append(group)

    return groups

source_groups = get_source_groups()


@client.on(events.NewMessage(chats=source_groups if source_groups else None))
async def handle_new_message(event):
    service = TelegramIngestionService()
    await service.ingest_event(event)


async def main():
    await client.start()
    me = await client.get_me()

    logger.info("Logged in as %s", me.username or me.id)
    logger.info("Listening to groups: %s", source_groups or "all visible chats")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())