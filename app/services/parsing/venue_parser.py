from __future__ import annotations

import re
from typing import Optional

from app.services.parsing.date_parser import strip_dates
from app.services.parsing.time_parser import strip_times

# Substrings that strongly indicate a venue name
_VENUE_KEYWORDS = re.compile(
    r"hall|sport|stadium|cc\b|centre|center|hub|pri\b|school|gym|arena|complex|park",
    re.IGNORECASE,
)

# Lines that should never be treated as venues (intent/noise phrases)
_NON_VENUE = re.compile(
    r"\b(?:let(?:ting)?\s+go|wts|wtb|sell(?:ing)?|transfer|buy(?:ing)?|"
    r"looking\s+(?:to|for)|find|swap(?:ping)?|court\s+to|at\s+cost|"
    r"pm\s+me|thank|priorit|interested|will\s+priorit|note:)\b"
    r"|^\s*[🙏]"
    r"|^\s*-\s+\w",
    re.IGNORECASE,
)

# Day-of-week tokens to strip when extracting venue from an inline line
_PAT_DAY_OF_WEEK = re.compile(
    r"\b(?:mon(?:day)?|tue(?:s(?:day)?)?|wed(?:nesday)?|thu(?:rs(?:day)?)?|"
    r"fri(?:day)?|sat(?:urday)?|sun(?:day)?)\b",
    re.IGNORECASE,
)

# Noise words that appear in inline lines but are not part of the venue
_PAT_NOISE = re.compile(
    r"\b(?:find|looking\s+for|lf|wtb|wts|court|badminton|slot|available|anywhere)\b",
    re.IGNORECASE,
)

# Trailing standalone price (last token that is a number)
_PAT_TRAILING_PRICE = re.compile(r"\$?\s*\d+(?:\.\d+)?\s*$")
_PAT_DOLLAR_PRICE = re.compile(r"\$\s*\d+(?:\.\d+)?")


def is_likely_venue(line: str) -> bool:
    """Return True if a block-format line looks like a venue name."""
    stripped = line.strip()
    if not stripped or len(stripped) < 2:
        return False
    if _NON_VENUE.search(stripped):
        return False
    if _VENUE_KEYWORDS.search(stripped):
        return True
    # Short lines with no digits and no special characters are likely venue shortnames
    # e.g. "Zhonghua pri", "sengkang", "anywhrre"
    words = stripped.split()
    if 1 <= len(words) <= 5 and not re.search(r"\d", stripped):
        return True
    return False


def extract_venue_from_inline(text: str) -> Optional[str]:
    """
    Extract a venue from a dense inline line that also contains a date,
    time, and possibly a price.  Strategy: strip everything that is
    unambiguously not the venue, then return what remains.
    """
    cleaned = strip_dates(text)
    cleaned = strip_times(cleaned)
    cleaned = _PAT_TRAILING_PRICE.sub("", cleaned)
    cleaned = _PAT_DOLLAR_PRICE.sub("", cleaned)
    cleaned = _PAT_DAY_OF_WEEK.sub("", cleaned)
    cleaned = _PAT_NOISE.sub("", cleaned)
    # Remove stray punctuation
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None
