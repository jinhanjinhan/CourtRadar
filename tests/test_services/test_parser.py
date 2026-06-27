import pytest

from app.services.parsing.parser import CourtTransferParser


@pytest.fixture
def parser():
    return CourtTransferParser()


def test_parse_sell_intent_wts(parser):
    result = parser.parse("WTS badminton court slot 8pm-10pm $15")
    assert result is not None
    assert result.intent == "sell"


def test_parse_sell_intent_selling(parser):
    result = parser.parse("Selling my badminton court this Saturday")
    assert result is not None
    assert result.intent == "sell"


def test_parse_sell_intent_transfer(parser):
    result = parser.parse("Transfer badminton court booking $20")
    assert result is not None
    assert result.intent == "sell"


def test_parse_sell_intent_letting_go(parser):
    result = parser.parse("Letting go badminton court slot")
    assert result is not None
    assert result.intent == "sell"


def test_parse_buy_intent_wtb(parser):
    result = parser.parse("WTB badminton court this weekend")
    assert result is not None
    assert result.intent == "buy"


def test_parse_buy_intent_looking_for(parser):
    result = parser.parse("Looking for a badminton court slot on Sunday")
    assert result is not None
    assert result.intent == "buy"


def test_parse_buy_intent_lf(parser):
    result = parser.parse("LF badminton court slot 7-9pm")
    assert result is not None
    assert result.intent == "buy"


def test_parse_unknown_intent(parser):
    result = parser.parse("Badminton court available for booking")
    assert result is not None
    assert result.intent == "unknown"


def test_parse_irrelevant_message_returns_none(parser):
    result = parser.parse("Anyone want to grab lunch today?")
    assert result is None


def test_parse_irrelevant_message_no_court_or_badminton(parser):
    result = parser.parse("WTS tennis racket $50")
    assert result is None


def test_parse_empty_string_returns_none(parser):
    result = parser.parse("")
    assert result is None


def test_parse_price_extraction_integer(parser):
    result = parser.parse("WTS badminton court $20")
    assert result is not None
    assert result.price == 20.0


def test_parse_price_extraction_decimal(parser):
    result = parser.parse("WTS badminton court $12.50")
    assert result is not None
    assert result.price == 12.5


def test_parse_price_extraction_without_dollar_sign(parser):
    result = parser.parse("WTS badminton court 15 per slot")
    assert result is not None
    assert result.price == 15.0


def test_parse_no_price_returns_none_price(parser):
    result = parser.parse("WTS badminton court slot, free!")
    assert result is not None
    # "free" has no numeric price pattern — price is None or some number
    # The parser matches digits; "free" has no digits so price should be None
    assert result.price is None


def test_parse_raw_text_preserved(parser):
    text = "WTS badminton court $10 this Saturday"
    result = parser.parse(text)
    assert result is not None
    assert result.raw_text == text


def test_parse_case_insensitive_keywords(parser):
    result = parser.parse("wts badminton court slot")
    assert result is not None
    assert result.intent == "sell"


def test_parse_court_keyword_triggers_parse(parser):
    result = parser.parse("WTS court slot available $8")
    assert result is not None
