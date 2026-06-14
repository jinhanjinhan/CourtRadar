from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from courtradar.core.config import settings
from courtradar.db.base import Base
from courtradar.db import models  # noqa: F401

engine = create_async_engine(settings.database_url, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


async def create_db_tables() -> None:
    if not settings.create_tables_on_startup:
        return

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

