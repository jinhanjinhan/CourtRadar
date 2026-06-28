from __future__ import annotations

from app.db.models import AlertPreference, ParsedListing


def listing_matches_alert(listing: ParsedListing, alert: AlertPreference) -> bool:
    if not alert.is_active:
        return False

    if alert.venue and alert.venue.lower() != listing.venue.lower():
        return False

    if (
        alert.max_price is not None
        and listing.price is not None
        and listing.price > alert.max_price
    ):
        return False

    if alert.earliest_time and listing.start_time < alert.earliest_time:
        return False

    if alert.latest_time and listing.end_time > alert.latest_time:
        return False

    return True
