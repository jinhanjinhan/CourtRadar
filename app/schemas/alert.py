from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertPreferenceBase(BaseModel):
    user_id: int
    venue: Optional[str] = None
    earliest_time: Optional[time] = None
    latest_time: Optional[time] = None
    max_price: Optional[float] = None


class AlertPreferenceCreate(AlertPreferenceBase):
    pass


class AlertPreferenceRead(AlertPreferenceBase):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
