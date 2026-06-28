from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    *,
    email: str,
    display_name: str,
    telegram_chat_id: Optional[str] = None,
) -> User:
    user = User(
        email=email, display_name=display_name, telegram_chat_id=telegram_chat_id
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
