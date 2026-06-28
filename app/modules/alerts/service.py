from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.modules.alerts import repository
from app.modules.alerts.schemas import AlertPreferenceCreate


async def create_alert_preference(
    session: AsyncSession, payload: AlertPreferenceCreate
):
    user = await session.get(User, payload.user_id)
    if user is None:
        raise ValueError("user not found")

    return await repository.create_alert_preference(
        session,
        user_id=payload.user_id,
        venue=payload.venue,
        earliest_time=payload.earliest_time,
        latest_time=payload.latest_time,
        max_price=payload.max_price,
    )


async def list_alert_preferences(session: AsyncSession, user_id: Optional[int] = None):
    return await repository.list_alert_preferences(session, user_id=user_id)
