from pydantic import BaseModel


class ParsedListing(BaseModel):
    venue: str
    date: str
    start_time: str
    end_time: str
    price: float | None = None
