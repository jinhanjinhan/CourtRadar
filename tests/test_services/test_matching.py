from datetime import time


from app.services.matching.engine import listing_matches_alert
from tests.factories import make_alert, make_listing


def test_all_none_alert_criteria_matches_any_listing():
    listing = make_listing()
    alert = make_alert()
    assert listing_matches_alert(listing, alert) is True


def test_inactive_alert_never_matches():
    listing = make_listing()
    alert = make_alert(is_active=False)
    assert listing_matches_alert(listing, alert) is False


def test_venue_match_is_case_insensitive():
    listing = make_listing(venue="Arena A")
    alert = make_alert(venue="arena a")
    assert listing_matches_alert(listing, alert) is True


def test_venue_mismatch_does_not_match():
    listing = make_listing(venue="Arena A")
    alert = make_alert(venue="Arena B")
    assert listing_matches_alert(listing, alert) is False


def test_none_alert_venue_matches_any_listing_venue():
    listing = make_listing(venue="Any Venue")
    alert = make_alert(venue=None)
    assert listing_matches_alert(listing, alert) is True


def test_price_within_limit_matches():
    listing = make_listing(price=10.0)
    alert = make_alert(max_price=20.0)
    assert listing_matches_alert(listing, alert) is True


def test_price_equal_to_limit_matches():
    listing = make_listing(price=20.0)
    alert = make_alert(max_price=20.0)
    assert listing_matches_alert(listing, alert) is True


def test_price_exceeds_limit_does_not_match():
    listing = make_listing(price=25.0)
    alert = make_alert(max_price=20.0)
    assert listing_matches_alert(listing, alert) is False


def test_none_listing_price_is_not_filtered_by_max_price():
    listing = make_listing(price=None)
    alert = make_alert(max_price=10.0)
    assert listing_matches_alert(listing, alert) is True


def test_none_alert_max_price_allows_any_listing_price():
    listing = make_listing(price=999.0)
    alert = make_alert(max_price=None)
    assert listing_matches_alert(listing, alert) is True


def test_start_time_at_or_after_earliest_matches():
    listing = make_listing(start_time=time(9, 0), end_time=time(11, 0))
    alert = make_alert(earliest_time=time(8, 0))
    assert listing_matches_alert(listing, alert) is True


def test_start_time_exactly_at_earliest_matches():
    listing = make_listing(start_time=time(8, 0), end_time=time(10, 0))
    alert = make_alert(earliest_time=time(8, 0))
    assert listing_matches_alert(listing, alert) is True


def test_start_time_before_earliest_does_not_match():
    listing = make_listing(start_time=time(7, 0), end_time=time(9, 0))
    alert = make_alert(earliest_time=time(8, 0))
    assert listing_matches_alert(listing, alert) is False


def test_end_time_at_or_before_latest_matches():
    listing = make_listing(start_time=time(9, 0), end_time=time(11, 0))
    alert = make_alert(latest_time=time(22, 0))
    assert listing_matches_alert(listing, alert) is True


def test_end_time_exactly_at_latest_matches():
    listing = make_listing(start_time=time(9, 0), end_time=time(22, 0))
    alert = make_alert(latest_time=time(22, 0))
    assert listing_matches_alert(listing, alert) is True


def test_end_time_after_latest_does_not_match():
    listing = make_listing(start_time=time(21, 0), end_time=time(23, 0))
    alert = make_alert(latest_time=time(22, 0))
    assert listing_matches_alert(listing, alert) is False


def test_none_earliest_time_does_not_filter_start_time():
    listing = make_listing(start_time=time(6, 0), end_time=time(8, 0))
    alert = make_alert(earliest_time=None)
    assert listing_matches_alert(listing, alert) is True


def test_none_latest_time_does_not_filter_end_time():
    listing = make_listing(start_time=time(22, 0), end_time=time(23, 59))
    alert = make_alert(latest_time=None)
    assert listing_matches_alert(listing, alert) is True


def test_all_criteria_satisfied_matches():
    listing = make_listing(venue="Test Venue", price=15.0, start_time=time(9, 0), end_time=time(11, 0))
    alert = make_alert(venue="Test Venue", max_price=20.0, earliest_time=time(8, 0), latest_time=time(22, 0))
    assert listing_matches_alert(listing, alert) is True


def test_one_criterion_fails_does_not_match():
    listing = make_listing(venue="Test Venue", price=15.0, start_time=time(9, 0), end_time=time(11, 0))
    alert = make_alert(venue="Other Venue", max_price=20.0, earliest_time=time(8, 0), latest_time=time(22, 0))
    assert listing_matches_alert(listing, alert) is False
