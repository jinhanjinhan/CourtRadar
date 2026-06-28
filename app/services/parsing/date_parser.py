from __future__ import annotations

import re
from datetime import date
from typing import Optional

_MONTH_MAP: dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5,
    "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

_MONTH_ALT = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may"
    r"|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?"
    r"|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

# "23 Jun (Tues)" or "23-Jun (Tue)"
_PAT_DAY_SEP_MONTH = re.compile(
    rf"\b(\d{{1,2}})[\s\-]({_MONTH_ALT})(?:\s*\([a-z]{{2,4}}\))?",
    re.IGNORECASE,
)

# "22jun" or "23jun" — no separator between day and month name
_PAT_DAY_NOSPACE_MONTH = re.compile(
    rf"\b(\d{{1,2}})({_MONTH_ALT})\b",
    re.IGNORECASE,
)

# "28/6" or "28/06"
_PAT_DAY_SLASH_MONTH = re.compile(r"\b(\d{1,2})/(\d{1,2})\b")


def contains_date(text: str) -> bool:
    return bool(
        _PAT_DAY_SEP_MONTH.search(text)
        or _PAT_DAY_NOSPACE_MONTH.search(text)
        or _PAT_DAY_SLASH_MONTH.search(text)
    )


def extract_date(text: str, reference_year: int = 2026) -> Optional[date]:
    m = _PAT_DAY_SEP_MONTH.search(text)
    if m:
        day = int(m.group(1))
        month = _MONTH_MAP.get(m.group(2).lower()[:3])
        if month:
            try:
                return date(reference_year, month, day)
            except ValueError:
                pass

    m = _PAT_DAY_NOSPACE_MONTH.search(text)
    if m:
        day = int(m.group(1))
        month = _MONTH_MAP.get(m.group(2).lower()[:3])
        if month:
            try:
                return date(reference_year, month, day)
            except ValueError:
                pass

    m = _PAT_DAY_SLASH_MONTH.search(text)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        try:
            return date(reference_year, month, day)
        except ValueError:
            pass

    return None


def strip_dates(text: str) -> str:
    """Remove all date tokens from text (used by venue extractor)."""
    text = _PAT_DAY_SEP_MONTH.sub("", text)
    text = _PAT_DAY_NOSPACE_MONTH.sub("", text)
    text = _PAT_DAY_SLASH_MONTH.sub("", text)
    return text
