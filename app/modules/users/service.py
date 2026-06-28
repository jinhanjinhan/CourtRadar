from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users import repository
from app.modules.users.schemas import UserCreate


async def create_user(session: AsyncSession, payload: UserCreate):
    existing_user = await repository.get_user_by_email(session, payload.email)
    if existing_user is not None:
        raise ValueError("email already exists")

    return await repository.create_user(
        session,
        email=payload.email,
        display_name=payload.display_name,
        telegram_chat_id=payload.telegram_chat_id,
    )


async def get_user(session: AsyncSession, user_id: int):
    return await repository.get_user_by_id(session, user_id)
