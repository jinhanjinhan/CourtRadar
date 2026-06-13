from pydantic import BaseModel


class AlertPreference(BaseModel):
    venue: str | None = None
    earliest_time: str | None = None
    latest_time: str | None = None
    max_price: float | None = None
