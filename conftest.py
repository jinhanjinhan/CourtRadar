import os

# Set required env vars before any app module is imported during test collection.
# The DB session is overridden in tests, so this URL is never actually connected to.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
