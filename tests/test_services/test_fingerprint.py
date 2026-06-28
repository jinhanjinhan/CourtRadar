from datetime import date, time


from app.services.parsing.fingerprint import make_fingerprint


def test_fingerprint_is_hex_string():
    fp = make_fingerprint(seller_id=1, venue="Venue A", listing_date=date(2024, 1, 15), start_time=time(8, 0), end_time=time(10, 0))
    assert isinstance(fp, str)
    assert len(fp) == 64  # SHA-256 hex digest length


def test_same_inputs_produce_same_fingerprint():
    kwargs = dict(seller_id=42, venue="Arena", listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    assert make_fingerprint(**kwargs) == make_fingerprint(**kwargs)


def test_different_seller_produces_different_fingerprint():
    base = dict(venue="Arena", listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    fp1 = make_fingerprint(seller_id=1, **base)
    fp2 = make_fingerprint(seller_id=2, **base)
    assert fp1 != fp2


def test_different_venue_produces_different_fingerprint():
    base = dict(seller_id=1, listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    fp1 = make_fingerprint(venue="Arena A", **base)
    fp2 = make_fingerprint(venue="Arena B", **base)
    assert fp1 != fp2


def test_different_date_produces_different_fingerprint():
    base = dict(seller_id=1, venue="Arena", start_time=time(9, 0), end_time=time(11, 0))
    fp1 = make_fingerprint(listing_date=date(2024, 6, 1), **base)
    fp2 = make_fingerprint(listing_date=date(2024, 6, 2), **base)
    assert fp1 != fp2


def test_different_start_time_produces_different_fingerprint():
    base = dict(seller_id=1, venue="Arena", listing_date=date(2024, 6, 1), end_time=time(11, 0))
    fp1 = make_fingerprint(start_time=time(9, 0), **base)
    fp2 = make_fingerprint(start_time=time(10, 0), **base)
    assert fp1 != fp2


def test_different_end_time_produces_different_fingerprint():
    base = dict(seller_id=1, venue="Arena", listing_date=date(2024, 6, 1), start_time=time(9, 0))
    fp1 = make_fingerprint(end_time=time(11, 0), **base)
    fp2 = make_fingerprint(end_time=time(12, 0), **base)
    assert fp1 != fp2


def test_none_seller_id_is_handled():
    fp = make_fingerprint(seller_id=None, venue="Arena", listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    assert isinstance(fp, str)
    assert len(fp) == 64


def test_none_venue_is_handled():
    fp = make_fingerprint(seller_id=1, venue=None, listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    assert isinstance(fp, str)


def test_all_none_fields_produces_consistent_fingerprint():
    fp1 = make_fingerprint(seller_id=None, venue=None, listing_date=None, start_time=None, end_time=None)
    fp2 = make_fingerprint(seller_id=None, venue=None, listing_date=None, start_time=None, end_time=None)
    assert fp1 == fp2


def test_court_number_affects_fingerprint():
    base = dict(seller_id=1, venue="Arena", listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    fp1 = make_fingerprint(court_number="1", **base)
    fp2 = make_fingerprint(court_number="2", **base)
    assert fp1 != fp2


def test_venue_case_normalized():
    base = dict(seller_id=1, listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    fp1 = make_fingerprint(venue="Arena A", **base)
    fp2 = make_fingerprint(venue="arena a", **base)
    assert fp1 == fp2


def test_venue_whitespace_normalized():
    base = dict(seller_id=1, listing_date=date(2024, 6, 1), start_time=time(9, 0), end_time=time(11, 0))
    fp1 = make_fingerprint(venue="  Arena  ", **base)
    fp2 = make_fingerprint(venue="Arena", **base)
    assert fp1 == fp2
