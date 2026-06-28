
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db import models  # noqa: F401

engine = create_async_engine(settings.database_url, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# `get_db_session()` removed — use `async_session` via `app.deps.db_session`.


# `create_db_tables()` was removed: table creation is handled by
# `scripts/create_tables.py` (manual/CI) and we don't run it on startup.
