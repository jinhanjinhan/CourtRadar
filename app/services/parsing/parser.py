import re
from dataclasses import dataclass
from datetime import date as date_cls, time as time_cls


@dataclass
class ParsedCourtTransfer:
    intent: str
    price: float | None
    raw_text: str
    # Structured slot fields. The current regex parser leaves these as None;
    # the Gemini parser is responsible for populating them. They feed both the
    # CourtTransfer row and its dedup fingerprint.
    venue: str | None = None
    listing_date: date_cls | None = None
    start_time: time_cls | None = None
    end_time: time_cls | None = None
    court_number: str | None = None


class CourtTransferParser:
    SELL_KEYWORDS = ["wts", "sell", "selling", "transfer", "letting go"]
    BUY_KEYWORDS = ["wtb", "buy", "looking for", "lf"]

    def parse(self, text: str) -> ParsedCourtTransfer | None:
        normalized = text.lower()

        if "badminton" not in normalized and "court" not in normalized:
            return None

        intent = "unknown"

        if any(keyword in normalized for keyword in self.SELL_KEYWORDS):
            intent = "sell"
        elif any(keyword in normalized for keyword in self.BUY_KEYWORDS):
            intent = "buy"

        return ParsedCourtTransfer(
            intent=intent,
            price=self._extract_price(normalized),
            raw_text=text,
        )

    def _extract_price(self, text: str) -> float | None:
        match = re.search(r"\$?\s*(\d+(?:\.\d+)?)", text)
        return float(match.group(1)) if match else None