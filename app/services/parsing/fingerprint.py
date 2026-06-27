"""Semantic fingerprint for court-transfer listings.

The fingerprint identifies a *listing*, not a *message*. The same seller often
cross-posts the identical slot to several Telegram groups with different wording,
so we hash the normalized structured identity rather than the raw text.

Price is deliberately excluded: a seller may lower the price on the same slot and
it is still the same listing.
"""

from __future__ import annotations

import hashlib
from datetime import date as date_cls, time as time_cls


def make_fingerprint(
    *,
    seller_id: int | None,
    venue: str | None,
    listing_date: date_cls | None,
    start_time: time_cls | None,
    end_time: time_cls | None,
    court_number: str | None = None,
) -> str:
    parts = [
        str(seller_id or ""),
        (venue or "").strip().lower(),
        listing_date.isoformat() if listing_date else "",
        start_time.isoformat() if start_time else "",
        end_time.isoformat() if end_time else "",
        (court_number or "").strip().lower(),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
