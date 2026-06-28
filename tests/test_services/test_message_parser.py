"""Tests for MessageParser against all five real-world message examples."""

import pytest
from datetime import date, time

from app.services.parsing.message_parser import MessageParser


@pytest.fixture
def parser():
    return MessageParser()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _times(listing) -> tuple[time, time]:
    return listing.start_time, listing.end_time


# ---------------------------------------------------------------------------
# Example 1 — block format, sell intent, single date/venue, three time slots
# ---------------------------------------------------------------------------

EXAMPLE_1 = """\
Court to let go

23 Jun (Tues)
Woodlands sports hall
1-3pm
3-4pm
5-6pm
"""


def test_ex1_returns_result(parser):
    result = parser.parse(EXAMPLE_1)
    assert result is not None


def test_ex1_intent(parser):
    assert parser.parse(EXAMPLE_1).intent == "sell"


def test_ex1_listing_count(parser):
    assert len(parser.parse(EXAMPLE_1).listings) == 3


def test_ex1_date(parser):
    for listing in parser.parse(EXAMPLE_1).listings:
        assert listing.listing_date == date(2026, 6, 23)


def test_ex1_venue(parser):
    for listing in parser.parse(EXAMPLE_1).listings:
        assert listing.venue is not None
        assert "woodlands" in listing.venue.lower()


def test_ex1_time_slots(parser):
    times = [_times(l) for l in parser.parse(EXAMPLE_1).listings]
    assert (time(13, 0), time(15, 0)) in times
    assert (time(15, 0), time(16, 0)) in times
    assert (time(17, 0), time(18, 0)) in times


# ---------------------------------------------------------------------------
# Example 2 — block format, sell intent, multiple date/venue blocks
# ---------------------------------------------------------------------------

EXAMPLE_2 = """\
Letting go court

23-Jun (Tue)
Clementi Sport Hall
7-8pm(1hr)

24-Jun (Wed)
Clementi Sport Hall
6-8pm

25-Jun (Thu)
The Frontier CC
6-8pm

27-Jun (Sat)
Jurong West Sport Hall
6-7pm(1hr)

27-Jun (Sat)
Jurong West Sport Hall
9-10pm(1hr)

28-Jun (Sun)
Jurong West Sport Hall
6-7pm(1hr)
"""


def test_ex2_returns_result(parser):
    result = parser.parse(EXAMPLE_2)
    assert result is not None


def test_ex2_intent(parser):
    assert parser.parse(EXAMPLE_2).intent == "sell"


def test_ex2_listing_count(parser):
    assert len(parser.parse(EXAMPLE_2).listings) == 6


def test_ex2_dates(parser):
    dates = [l.listing_date for l in parser.parse(EXAMPLE_2).listings]
    assert date(2026, 6, 23) in dates
    assert date(2026, 6, 24) in dates
    assert date(2026, 6, 25) in dates
    assert dates.count(date(2026, 6, 27)) == 2
    assert date(2026, 6, 28) in dates


def test_ex2_venues(parser):
    venues = [l.venue for l in parser.parse(EXAMPLE_2).listings]
    assert any("clementi" in (v or "").lower() for v in venues)
    assert any("frontier" in (v or "").lower() for v in venues)
    assert any("jurong" in (v or "").lower() for v in venues)


def test_ex2_23jun_time(parser):
    listing = next(
        l for l in parser.parse(EXAMPLE_2).listings if l.listing_date == date(2026, 6, 23)
    )
    assert listing.start_time == time(19, 0)
    assert listing.end_time == time(20, 0)


# ---------------------------------------------------------------------------
# Example 3 — single inline line, buy intent
# ---------------------------------------------------------------------------

EXAMPLE_3 = "Find 27 june court 7-9pm anywhrre"


def test_ex3_returns_result(parser):
    assert parser.parse(EXAMPLE_3) is not None


def test_ex3_intent(parser):
    assert parser.parse(EXAMPLE_3).intent == "buy"


def test_ex3_listing_count(parser):
    assert len(parser.parse(EXAMPLE_3).listings) == 1


def test_ex3_date(parser):
    listing = parser.parse(EXAMPLE_3).listings[0]
    assert listing.listing_date == date(2026, 6, 27)


def test_ex3_time(parser):
    listing = parser.parse(EXAMPLE_3).listings[0]
    assert listing.start_time == time(19, 0)
    assert listing.end_time == time(21, 0)


def test_ex3_venue(parser):
    listing = parser.parse(EXAMPLE_3).listings[0]
    assert listing.venue is not None
    assert "anywhrre" in listing.venue.lower()


# ---------------------------------------------------------------------------
# Example 4 — swap intent, block format, swap time detection
# ---------------------------------------------------------------------------

EXAMPLE_4 = """\
Looking to swap

28/6 sun
Zhonghua pri
Have 2-3, to swap with 1-2
"""


def test_ex4_returns_result(parser):
    assert parser.parse(EXAMPLE_4) is not None


def test_ex4_intent(parser):
    assert parser.parse(EXAMPLE_4).intent == "swap"


def test_ex4_listing_count(parser):
    assert len(parser.parse(EXAMPLE_4).listings) == 1


def test_ex4_date(parser):
    listing = parser.parse(EXAMPLE_4).listings[0]
    assert listing.listing_date == date(2026, 6, 28)


def test_ex4_venue(parser):
    listing = parser.parse(EXAMPLE_4).listings[0]
    assert listing.venue is not None
    assert "zhonghua" in listing.venue.lower()


def test_ex4_swap_have(parser):
    listing = parser.parse(EXAMPLE_4).listings[0]
    assert listing.swap_have_start == time(14, 0)
    assert listing.swap_have_end == time(15, 0)


def test_ex4_swap_want(parser):
    listing = parser.parse(EXAMPLE_4).listings[0]
    assert listing.swap_want_start == time(13, 0)
    assert listing.swap_want_end == time(14, 0)


# ---------------------------------------------------------------------------
# Example 5 — inline format, sell intent, multiple dates/venues/prices
# ---------------------------------------------------------------------------

EXAMPLE_5 = """\
Court to let go at cost:

22jun mon 6-8pm sengkang 14.8

23jun tues 4-6pm tampines hub 7
23jun tues 6-8pm jurong west 14.8

24jun wed 5-7pm tampines hub 10.9

25jun thurs 6-8pm sengkang 14.8

26jun fri 5-6pm tampines hub 3.5
26jun fri 9-10pm jurong west 7.4
26jun fri 6-8pm sengkang 14.8



\U0001f64fWill prioritise user who have courts to swap:
- jurong west
- tampines hub
- yio chu kang

PM me if interested. Thank you!j
"""


def test_ex5_returns_result(parser):
    assert parser.parse(EXAMPLE_5) is not None


def test_ex5_intent(parser):
    assert parser.parse(EXAMPLE_5).intent == "sell"


def test_ex5_listing_count(parser):
    assert len(parser.parse(EXAMPLE_5).listings) == 8


def test_ex5_first_listing(parser):
    listing = parser.parse(EXAMPLE_5).listings[0]
    assert listing.listing_date == date(2026, 6, 22)
    assert listing.start_time == time(18, 0)
    assert listing.end_time == time(20, 0)
    assert listing.price == pytest.approx(14.8)
    assert "sengkang" in (listing.venue or "").lower()


def test_ex5_prices_present(parser):
    listings = parser.parse(EXAMPLE_5).listings
    prices = [l.price for l in listings]
    assert pytest.approx(14.8) in prices
    assert pytest.approx(7.0) in prices
    assert pytest.approx(10.9) in prices
    assert pytest.approx(3.5) in prices
    assert pytest.approx(7.4) in prices


def test_ex5_footer_lines_excluded(parser):
    # "jurong west", "tampines hub" footer lines must not create extra listings
    assert len(parser.parse(EXAMPLE_5).listings) == 8


def test_ex5_venues(parser):
    venues = [(l.venue or "").lower() for l in parser.parse(EXAMPLE_5).listings]
    assert any("sengkang" in v for v in venues)
    assert any("tampines" in v for v in venues)
    assert any("jurong" in v for v in venues)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_string_returns_none(parser):
    assert parser.parse("") is None


def test_whitespace_only_returns_none(parser):
    assert parser.parse("   \n\n  ") is None


def test_unrelated_message_returns_none(parser):
    assert parser.parse("Anyone want to grab lunch today?") is None


def test_tennis_message_returns_none(parser):
    assert parser.parse("WTS tennis racket $50") is None
