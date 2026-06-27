import logging

from app.db.session import async_session
from app.services.ingestion.telegram_ingestion.repository import (
    insert_message_if_new,
    upsert_court_transfer,
)
from app.services.parsing.fingerprint import make_fingerprint
from app.services.parsing.parser import CourtTransferParser

logger = logging.getLogger(__name__)


class TelegramIngestionService:
    def __init__(self):
        self.parser = CourtTransferParser()

    async def process_message(self, message, topic_id: int | None = None) -> None:
        """Idempotently ingest a single Telegram message.

        Shared by the live event handler and the startup backfill. Both paths are
        at-least-once; the unique constraints below make double delivery a no-op,
        so overlap between backfill and the live stream is harmless.
        """
        text = (message.message or "").strip()
        if not text:
            return

        is_new_listing = False

        # One atomic transaction: the raw message row and the parsed listing row
        # commit together, so the backfill watermark (max message id) only
        # advances for messages that were processed end to end. A crash before
        # commit leaves nothing persisted and the message is re-fetched on
        # restart.
        async with async_session() as session:
            async with session.begin():
                is_new_message = await insert_message_if_new(
                    session,
                    chat_id=message.chat_id,
                    message_id=message.id,
                    topic_id=topic_id,
                    sender_id=message.sender_id,
                    text=text,
                    message_date=message.date,
                )
                if not is_new_message:
                    return  # already ingested on a previous run

                parsed = self.parser.parse(text)
                if parsed is None:
                    logger.info("Irrelevant message id=%s", message.id)
                    return

                fingerprint = make_fingerprint(
                    seller_id=message.sender_id,
                    venue=parsed.venue,
                    listing_date=parsed.listing_date,
                    start_time=parsed.start_time,
                    end_time=parsed.end_time,
                    court_number=parsed.court_number,
                )

                is_new_listing = await upsert_court_transfer(
                    session,
                    fingerprint=fingerprint,
                    seller_id=message.sender_id,
                    intent=parsed.intent,
                    venue=parsed.venue,
                    date=parsed.listing_date,
                    start_time=parsed.start_time,
                    end_time=parsed.end_time,
                    court_number=parsed.court_number,
                    price=parsed.price,
                )

        # Side effects run only after the transaction commits and only for a
        # genuinely new listing, so a cross-posted slot notifies users once.
        if is_new_listing:
            logger.info("New court transfer ingested (fingerprint=%s)", fingerprint)
            # Matching + notification dispatch hook in here.
