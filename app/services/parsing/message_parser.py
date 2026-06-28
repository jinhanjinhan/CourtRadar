"""
MessageParser — top-level orchestrator.

Parses a raw free-text message and returns a ParsedMessage that contains
one CourtListing per court slot mentioned.  Supports two structural layouts:

  Block format   — date on its own line, venue on next, then ≥1 time lines
  Inline format  — each listing on a single line: date + time [+ venue] [+ price]

The format is detected automatically: if most date-bearing lines also carry a
time token on the same line → inline, otherwise → block.
"""

from __future__ import annotations

import re
from datetime import date as date_cls
from typing import Optional

from app.services.parsing.models import CourtListing, ParsedMessage
from app.services.parsing.intent_parser import detect_intent
from app.services.parsing.date_parser import contains_date, extract_date
from app.services.parsing.time_parser import (
    contains_time,
    extract_time_slots,
    extract_swap_times,
)
from app.services.parsing.venue_parser import is_likely_venue, extract_venue_from_inline
from app.services.parsing.price_parser import extract_price, is_price_only

# Keywords that confirm a message is about badminton court transfers.
# Intentionally excludes generic keywords like "wts"/"wtb" which could
# appear in unrelated messages ("WTS tennis racket").
_COURT_KEYWORDS = re.compile(
    r"\b(?:badminton|court|swap|let(?:ting)?\s+go|transfer)\b",
    re.IGNORECASE,
)

# Lines that carry no useful listing information and should be skipped
_SKIP_LINE = re.compile(
    r"^\s*(?:pm\s+me|thank|priorit|🙏|will\s+priorit|note:|please|interested"
    r"|pm\s+if|generated\s+with)"
    r"|^\s*-\s+\w",
    re.IGNORECASE,
)


def _should_skip(line: str) -> bool:
    return bool(_SKIP_LINE.search(line.strip()))


class MessageParser:
    """
    Parse a raw message into a :class:`ParsedMessage`.

    Returns ``None`` when the message is empty or unrelated to court transfers.
    """

    def parse(self, text: str) -> Optional[ParsedMessage]:
        if not text or not text.strip():
            return None
        if not _COURT_KEYWORDS.search(text):
            return None

        intent = detect_intent(text)
        non_empty = [
            (i, ln.rstrip()) for i, ln in enumerate(text.splitlines()) if ln.strip()
        ]
        listings = self._extract_listings(non_empty, intent, text)

        return ParsedMessage(raw_text=text, intent=intent, listings=listings)

    # ------------------------------------------------------------------
    # Format detection
    # ------------------------------------------------------------------

    def _extract_listings(
        self,
        non_empty: list[tuple[int, str]],
        intent: str,
        raw_text: str,
    ) -> list[CourtListing]:
        inline_count = sum(
            1 for _, ln in non_empty if contains_date(ln) and contains_time(ln)
        )
        block_date_count = sum(
            1 for _, ln in non_empty if contains_date(ln) and not contains_time(ln)
        )
        if inline_count > block_date_count:
            return self._parse_inline(non_empty, intent, raw_text)
        return self._parse_block(non_empty, intent, raw_text)

    # ------------------------------------------------------------------
    # Inline strategy  ("22jun mon 6-8pm sengkang 14.8")
    # ------------------------------------------------------------------

    def _parse_inline(
        self,
        non_empty: list[tuple[int, str]],
        intent: str,
        raw_text: str,
    ) -> list[CourtListing]:
        listings: list[CourtListing] = []
        for _, line in non_empty:
            if _should_skip(line):
                continue
            if not (contains_date(line) and contains_time(line)):
                continue

            listing_date = extract_date(line)
            time_slots = extract_time_slots(line)
            venue = extract_venue_from_inline(line)
            price = extract_price(line)

            for start, end in time_slots:
                listings.append(
                    CourtListing(
                        intent=intent,
                        raw_text=raw_text,
                        listing_date=listing_date,
                        start_time=start,
                        end_time=end,
                        venue=venue,
                        price=price,
                    )
                )
        return listings

    # ------------------------------------------------------------------
    # Block strategy  (date line → venue line → time line(s))
    # ------------------------------------------------------------------

    def _parse_block(
        self,
        non_empty: list[tuple[int, str]],
        intent: str,
        raw_text: str,
    ) -> list[CourtListing]:
        listings: list[CourtListing] = []
        current_date: Optional[date_cls] = None
        current_venue: Optional[str] = None

        for _, line in non_empty:
            stripped = line.strip()
            if _should_skip(stripped):
                continue

            has_date = contains_date(stripped)
            has_time = contains_time(stripped)

            if has_date and not has_time:
                # Start of a new date block
                current_date = extract_date(stripped)
                current_venue = None
                continue

            if has_time:
                # For swap messages, try to detect "have X / want Y" first
                if intent == "swap":
                    have_slot, want_slot = extract_swap_times(stripped)
                    if have_slot or want_slot:
                        listings.append(
                            CourtListing(
                                intent=intent,
                                raw_text=raw_text,
                                listing_date=current_date,
                                venue=current_venue,
                                start_time=have_slot[0] if have_slot else None,
                                end_time=have_slot[1] if have_slot else None,
                                swap_have_start=have_slot[0] if have_slot else None,
                                swap_have_end=have_slot[1] if have_slot else None,
                                swap_want_start=want_slot[0] if want_slot else None,
                                swap_want_end=want_slot[1] if want_slot else None,
                            )
                        )
                        continue

                time_slots = extract_time_slots(stripped)
                price = extract_price(stripped)

                for start, end in time_slots:
                    listings.append(
                        CourtListing(
                            intent=intent,
                            raw_text=raw_text,
                            listing_date=current_date,
                            venue=current_venue,
                            start_time=start,
                            end_time=end,
                            price=price,
                        )
                    )
                continue

            if is_price_only(stripped):
                # Standalone price line — update the most recently added listing
                price = extract_price(stripped)
                if listings and price is not None:
                    listings[-1].price = price
                continue

            if is_likely_venue(stripped):
                current_venue = stripped
                continue

        return listings
