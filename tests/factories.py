from datetime import datetime, time, timezone

from app.db.models import AlertPreference, ParsedListing, User


def make_user(
    id: int = 1,
    email: str = "test@example.com",
    display_name: str = "Test User",
    telegram_chat_id: str | None = None,
    created_at: datetime | None = None,
) -> User:
    user = User()
    user.id = id
    user.email = email
    user.display_name = display_name
    user.telegram_chat_id = telegram_chat_id
    user.created_at = created_at or datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


def make_alert(
    id: int = 1,
    user_id: int = 1,
    venue: str | None = None,
    earliest_time: time | None = None,
    latest_time: time | None = None,
    max_price: float | None = None,
    is_active: bool = True,
    created_at: datetime | None = None,
) -> AlertPreference:
    alert = AlertPreference()
    alert.id = id
    alert.user_id = user_id
    alert.venue = venue
    alert.earliest_time = earliest_time
    alert.latest_time = latest_time
    alert.max_price = max_price
    alert.is_active = is_active
    alert.created_at = created_at or datetime(2024, 1, 1, tzinfo=timezone.utc)
    return alert


def make_listing(
    id: int = 1,
    source_channel: str = "test_channel",
    raw_text: str = "WTS badminton court 8pm-10pm $10",
    venue: str = "Test Venue",
    listing_date: str = "2024-01-15",
    start_time: time | None = None,
    end_time: time | None = None,
    price: float | None = 10.0,
    created_at: datetime | None = None,
) -> ParsedListing:
    listing = ParsedListing()
    listing.id = id
    listing.source_channel = source_channel
    listing.raw_text = raw_text
    listing.venue = venue
    listing.listing_date = listing_date
    listing.start_time = start_time or time(20, 0)
    listing.end_time = end_time or time(22, 0)
    listing.price = price
    listing.created_at = created_at or datetime(2024, 1, 1, tzinfo=timezone.utc)
    return listing
