from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParsedListingBase(BaseModel):
    source_channel: str
    raw_text: str
    venue: str
    listing_date: str
    start_time: time
    end_time: time
    price: Optional[float] = None


class ParsedListingCreate(ParsedListingBase):
    pass


class ParsedListingRead(ParsedListingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
