from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel


class ParsedListingCreate(BaseModel):
    source_channel: str
    raw_text: str
    venue: str
    listing_date: str
    start_time: time
    end_time: time
    price: Optional[float] = None


class ParsedListingRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    source_channel: str
    raw_text: str
    venue: str
    listing_date: str
    start_time: time
    end_time: time
    price: Optional[float]
    created_at: datetime
