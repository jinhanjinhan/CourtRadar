from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "CourtRadar"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    telegram_api_id: Optional[int] = None
    telegram_api_hash: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    sg_badminton_group_one_id: Optional[int] = None
    sg_badminton_group_two_id: Optional[int] = None
    sg_badminton_group_three_id: Optional[int] = None
    sg_badminton_group_one_topic_id: Optional[int] = None
    sg_badminton_group_two_topic_id: Optional[int] = None
    sg_badminton_group_three_topic_id: Optional[int] = None
    gemini_api_key: Optional[str] = None
    create_tables_on_startup: bool = False

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
