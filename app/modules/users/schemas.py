from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    display_name: str
    telegram_chat_id: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: str
    display_name: str
    telegram_chat_id: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
