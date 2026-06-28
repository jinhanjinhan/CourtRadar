from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as date_cls, time as time_cls


@dataclass
class CourtListing:
    """A single extracted court slot from a message."""

    intent: str  # "sell" | "buy" | "swap" | "unknown"
    raw_text: str
    venue: str | None = None
    listing_date: date_cls | None = None
    start_time: time_cls | None = None
    end_time: time_cls | None = None
    court_number: str | None = None
    price: float | None = None
    # Swap-specific: the slot offered vs the slot wanted
    swap_have_start: time_cls | None = None
    swap_have_end: time_cls | None = None
    swap_want_start: time_cls | None = None
    swap_want_end: time_cls | None = None


@dataclass
class ParsedMessage:
    """All structured listings extracted from a single raw message."""

    raw_text: str
    intent: str  # primary intent detected from the message header
    listings: list[CourtListing] = field(default_factory=list)
