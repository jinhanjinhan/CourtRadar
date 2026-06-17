from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CourtRadar"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    telegram_api_id: Optional[str] = None
    telegram_api_hash: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    gemini_api_key: Optional[str] = None
    create_tables_on_startup: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
