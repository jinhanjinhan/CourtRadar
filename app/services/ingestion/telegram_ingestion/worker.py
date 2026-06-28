import asyncio
import logging

from telethon import events

from app.core.config import settings
from app.db.session import async_session
from app.services.ingestion.telegram_ingestion.repository import (
    get_last_seen_message_id,
)
from app.services.ingestion.telegram_ingestion.telegram_client import client
from app.services.ingestion.telegram_ingestion.service import TelegramIngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service = TelegramIngestionService()


def topic_set(topic_id: int | None) -> set[int] | None:
    if topic_id is None:
        return None
    return {topic_id}


_raw_group_rules: dict[int | None, set[int] | None] = {
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

GROUP_TOPIC_RULES: dict[int, set[int] | None] = {
    group_id: topic_ids
    for group_id, topic_ids in _raw_group_rules.items()
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
            "[live] Skipping message_id=%s chat_id=%s topic_id=%s",
            message.id,
            chat_id,
            topic_id,
        )
        return

    logger.info(
        "[live] Processing message_id=%s chat_id=%s topic_id=%s",
        message.id,
        chat_id,
        topic_id,
    )

    await service.process_message(message, topic_id=topic_id)


async def backfill(chat_id: int) -> None:
    """Replay messages posted while the worker was down.

    The live `events.NewMessage` handler only sees messages that arrive while
    connected, so on every startup we fetch the gap between our high-watermark
    (the newest stored message id for this chat) and now. `reverse=True` walks
    oldest -> newest so the watermark advances monotonically, and ingestion is
    idempotent so any overlap with the live stream is dropped by the unique
    constraints.
    """
    async with async_session() as session:
        since = await get_last_seen_message_id(session, chat_id)

    logger.info(
        "[backfill] Starting chat_id=%s from message_id>%s",
        chat_id,
        since,
    )

    processed = 0
    skipped = 0
    async for message in client.iter_messages(chat_id, min_id=since, reverse=True):
        topic_id = get_topic_id(message)

        if not should_process_message(chat_id=chat_id, topic_id=topic_id):
            logger.info(
                "[backfill] Skipping message_id=%s chat_id=%s topic_id=%s",
                message.id,
                chat_id,
                topic_id,
            )
            skipped += 1
            continue

        logger.info(
            "[backfill] Processing message_id=%s chat_id=%s topic_id=%s",
            message.id,
            chat_id,
            topic_id,
        )
        await service.process_message(message, topic_id=topic_id)
        processed += 1

    logger.info(
        "[backfill] Complete chat_id=%s processed=%s skipped=%s",
        chat_id,
        processed,
        skipped,
    )


async def main():
    await client.start()
    me = await client.get_me()

    logger.info("Logged in as %s", me.username or me.id)
    logger.info("Listening to groups: %s", source_groups)
    logger.info("Group topic rules: %s", GROUP_TOPIC_RULES)

    # Startup ordering — IMPORTANT: backfill and live processing run
    # CONCURRENTLY (interleaved on the single asyncio event loop), NOT strictly
    # one-then-the-other:
    #
    #   - The live `handle_new_message` handler is already registered (via the
    #     @client.on decorator at import time). As soon as `client.start()` above
    #     connects, Telethon begins dispatching incoming messages as event-loop
    #     tasks.
    #   - The backfill loop below is kicked off first in source order, but it
    #     spends most of its time *awaiting* I/O (iter_messages fetches, DB
    #     writes). Each `await` is a yield point where the loop is free to run a
    #     pending live handler task. So a message arriving DURING backfill is
    #     processed in between backfill's await points — not queued until
    #     backfill finishes.
    #
    # This interleaving is safe precisely because ingestion is idempotent: a live
    # message and a backfilled message can even be the same row, and the unique
    # constraints (telegram_messages + court_transfers.fingerprint) drop the
    # duplicate. We do not need a clean handoff between the two paths.
    for chat_id in source_groups:
        await backfill(chat_id)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
