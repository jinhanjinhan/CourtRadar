from __future__ import annotations

import asyncio
import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.base import Base
from app.core.config import settings
import app.db.models  # noqa: F401  # ensure model classes are registered
from sqlalchemy.ext.asyncio import create_async_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create CourtRadar database tables.")
    parser.add_argument(
        "--database-url",
        help="Override the database URL for this run instead of using DATABASE_URL from the environment.",
    )
    return parser.parse_args()


async def create_tables() -> None:
    args = parse_args()
    database_url = args.database_url or settings.database_url
    engine = create_async_engine(database_url, future=True)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(create_tables())
    print("Created database tables successfully.")


if __name__ == "__main__":
    main()
