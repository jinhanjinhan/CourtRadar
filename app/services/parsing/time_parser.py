from __future__ import annotations

import re
from datetime import time
from typing import Optional

# Matches "1-3pm", "7-8pm(1hr)", "6-8pm", "2-3", "1:30-3:00pm", "9-10pm"
# The meridiem (am/pm) at the end applies to both ends of the range.
_PAT_TIME_RANGE = re.compile(
    r"\b(\d{1,2})(?::(\d{2}))?\s*[-–]\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b",
    re.IGNORECASE,
)

# Matches inline "have X-Y" and "swap with X-Y" patterns for swap listings
_PAT_SWAP_HAVE = re.compile(
    r"have\s+(\d{1,2}(?::\d{2})?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
    re.IGNORECASE,
)
_PAT_SWAP_WANT = re.compile(
    r"(?:swap\s+with|want)\s+(\d{1,2}(?::\d{2})?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
    re.IGNORECASE,
)


def _to_24h(hour: int, meridiem: Optional[str]) -> int:
    """Convert hour to 24-hour format. With no meridiem, assumes PM (badminton context)."""
    if meridiem and meridiem.lower() == "am":
        return 0 if hour == 12 else hour
    if meridiem and meridiem.lower() == "pm":
        return hour if hour == 12 else hour + 12
    # No meridiem: assume PM for typical court hours
    return hour if hour >= 12 else hour + 12


def contains_time(text: str) -> bool:
    return bool(_PAT_TIME_RANGE.search(text))


def extract_time_slots(text: str) -> list[tuple[time, time]]:
    """Return all (start, end) time pairs found in text."""
    results = []
    for m in _PAT_TIME_RANGE.finditer(text):
        start_h = int(m.group(1))
        start_min = int(m.group(2) or 0)
        end_h = int(m.group(3))
        end_min = int(m.group(4) or 0)
        meridiem = m.group(5)

        try:
            start = time(_to_24h(start_h, meridiem), start_min)
            end = time(_to_24h(end_h, meridiem), end_min)
            results.append((start, end))
        except ValueError:
            continue

    return results


def extract_swap_times(
    text: str,
) -> tuple[Optional[tuple[time, time]], Optional[tuple[time, time]]]:
    """
    Parse "Have X-Y, to swap with A-B" patterns.
    Returns (have_slot, want_slot), either of which may be None.
    """
    have_slot: Optional[tuple[time, time]] = None
    want_slot: Optional[tuple[time, time]] = None

    m = _PAT_SWAP_HAVE.search(text)
    if m:
        slots = extract_time_slots(m.group(1))
        if slots:
            have_slot = slots[0]

    m = _PAT_SWAP_WANT.search(text)
    if m:
        slots = extract_time_slots(m.group(1))
        if slots:
            want_slot = slots[0]

    return have_slot, want_slot


def strip_times(text: str) -> str:
    """Remove all time range tokens and duration annotations from text."""
    text = _PAT_TIME_RANGE.sub("", text)
    text = re.sub(r"\(\s*\d+\s*hr\s*\)", "", text, flags=re.IGNORECASE)
    return text
