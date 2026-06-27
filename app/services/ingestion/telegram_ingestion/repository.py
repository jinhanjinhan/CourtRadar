"""Idempotent persistence helpers for Telegram ingestion.

Every write uses Postgres ``ON CONFLICT DO NOTHING`` and reports back, via the
``RETURNING`` clause, whether the row was actually inserted. Callers use that
boolean to fire side effects (matching, notifications) exactly once.

These helpers do not commit; run them inside a ``session.begin()`` block so the
message row and the transfer row land in a single atomic transaction.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CourtTransfer, TelegramMessage


async def get_last_seen_message_id(session: AsyncSession, chat_id: int) -> int:
    """High-watermark for backfill: the newest message id already stored."""
    result = await session.execute(
        select(func.max(TelegramMessage.telegram_message_id)).where(
            TelegramMessage.telegram_chat_id == chat_id
        )
    )
    return result.scalar() or 0


async def insert_message_if_new(
    session: AsyncSession,
    *,
    chat_id: int,
    message_id: int,
    topic_id: int | None,
    sender_id: int | None,
    text: str,
    message_date: datetime,
) -> bool:
    """Transport-level idempotency. Returns True only on a genuine insert."""
    stmt = (
        pg_insert(TelegramMessage)
        .values(
            telegram_chat_id=chat_id,
            telegram_message_id=message_id,
            telegram_topic_id=topic_id,
            sender_id=sender_id,
            text=text,
            message_date=message_date,
        )
        .on_conflict_do_nothing(constraint="uq_telegram_chat_message")
        .returning(TelegramMessage.id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def upsert_court_transfer(
    session: AsyncSession,
    *,
    fingerprint: str,
    seller_id: int | None,
    intent: str,
    venue: str | None,
    date,
    start_time,
    end_time,
    court_number: str | None,
    price,
) -> bool:
    """Semantic dedup. Returns True only for a brand-new listing."""
    stmt = (
        pg_insert(CourtTransfer)
        .values(
            fingerprint=fingerprint,
            seller_id=seller_id,
            intent=intent,
            venue=venue,
            date=date,
            start_time=start_time,
            end_time=end_time,
            court_number=court_number,
            price=price,
        )
        .on_conflict_do_nothing(index_elements=["fingerprint"])
        .returning(CourtTransfer.id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None
