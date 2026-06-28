from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AlertPreference


async def create_alert_preference(
    session: AsyncSession,
    *,
    user_id: int,
    venue: Optional[str],
    earliest_time,
    latest_time,
    max_price: Optional[float],
) -> AlertPreference:
    alert = AlertPreference(
        user_id=user_id,
        venue=venue,
        earliest_time=earliest_time,
        latest_time=latest_time,
        max_price=max_price,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


async def list_alert_preferences(
    session: AsyncSession, user_id: Optional[int] = None
) -> list[AlertPreference]:
    query = select(AlertPreference)
    if user_id is not None:
        query = query.where(AlertPreference.user_id == user_id)
    result = await session.execute(query.order_by(AlertPreference.id.desc()))
    return list(result.scalars().all())


async def list_active_alert_preferences(session: AsyncSession) -> list[AlertPreference]:
    result = await session.execute(
        select(AlertPreference)
        .where(AlertPreference.is_active.is_(True))
        .order_by(AlertPreference.id.desc())
    )
    return list(result.scalars().all())
