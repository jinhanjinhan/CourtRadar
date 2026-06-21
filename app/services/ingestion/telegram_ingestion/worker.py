import asyncio
import logging

from telethon import events

from app.core.config import settings
from app.services.ingestion.telegram_ingestion.telegram_client import client
from app.services.ingestion.telegram_ingestion.service import TelegramIngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def topic_set(topic_id: int | None) -> set[int] | None:
    if topic_id is None:
        return None
    return {topic_id}


GROUP_TOPIC_RULES: dict[int, set[int] | None] = {
    settings.sg_badminton_group_one_id: topic_set(
        settings.sg_badminton_group_one_topic_id
    ),
    settings.sg_badminton_group_two_id: topic_set(
        settings.sg_badminton_group_two_topic_id
    ),
    settings.sg_badminton_group_three_id: topic_set(
        settings.sg_badminton_group_three_topic_id
    ),
}

GROUP_TOPIC_RULES = {
    group_id: topic_ids
    for group_id, topic_ids in GROUP_TOPIC_RULES.items()
    if group_id is not None
}

source_groups = list(GROUP_TOPIC_RULES.keys())


def get_topic_id(message) -> int | None:
    reply_to = getattr(message, "reply_to", None)

    if reply_to is None:
        return None

    reply_to_msg_id = getattr(reply_to, "reply_to_msg_id", None)
    if reply_to_msg_id is not None:
        return reply_to_msg_id

    reply_to_top_id = getattr(reply_to, "reply_to_top_id", None)
    if reply_to_top_id is not None:
        return reply_to_top_id

    return None


def should_process_message(chat_id: int, topic_id: int | None) -> bool:

    # Check if the chat_id is in our rules
    allowed_topics = GROUP_TOPIC_RULES.get(chat_id)

    # Chat is not configured at all.
    if chat_id not in GROUP_TOPIC_RULES:
        return False

    # Chat is configured, but no topic restriction. E.g. SG BADMINTON COURT
    # Process all messages from this chat.
    if allowed_topics is None:
        return True

    # Chat is configured with specific allowed topics.
    return topic_id in allowed_topics



@client.on(events.NewMessage(chats=source_groups))
async def handle_new_message(event):
    message = event.message
    chat_id = message.chat_id
    topic_id = get_topic_id(message)

    if not should_process_message(chat_id=chat_id, topic_id=topic_id):
        logger.info(
            "Skipping message_id=%s chat_id=%s topic_id=%s",
            message.id,
            chat_id,
            topic_id,
        )
        return

    logger.info(
        "Processing message_id=%s chat_id=%s topic_id=%s",
        message.id,
        chat_id,
        topic_id,
    )

    service = TelegramIngestionService()
    await service.ingest_event(event)



async def main():
    await client.start()
    me = await client.get_me()

    logger.info("Logged in as %s", me.username or me.id)
    logger.info("Listening to groups: %s", source_groups)
    logger.info("Group topic rules: %s", GROUP_TOPIC_RULES)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
