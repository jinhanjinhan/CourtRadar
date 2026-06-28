from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel


class AlertPreferenceCreate(BaseModel):
    user_id: int
    venue: Optional[str] = None
    earliest_time: Optional[time] = None
    latest_time: Optional[time] = None
    max_price: Optional[float] = None


class AlertPreferenceRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    venue: Optional[str]
    earliest_time: Optional[time]
    latest_time: Optional[time]
    max_price: Optional[float]
    is_active: bool
    created_at: datetime
