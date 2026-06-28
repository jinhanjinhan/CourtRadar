from __future__ import annotations

import re
from typing import Optional

# Matches "$14.8", "14.8", "7" — requires trailing space or end-of-string to
# avoid greedily matching the day part of a date like "22jun".
_PAT_PRICE = re.compile(
    r"\$\s*(\d+(?:\.\d+)?)"
    r"|(?<!\d)(\d+(?:\.\d+)?)\s*(?:per\s+(?:slot|hr|hour))?(?=\s|$)",
)

# A line that is *only* a standalone price, e.g. "14.8" or "$7"
_PAT_PRICE_ONLY = re.compile(
    r"^\$?\s*\d+(?:\.\d+)?\s*(?:per\s+(?:slot|hr|hour))?\s*$",
    re.IGNORECASE,
)


def extract_price(text: str) -> Optional[float]:
    for m in _PAT_PRICE.finditer(text):
        val = m.group(1) or m.group(2)
        if val:
            return float(val)
    return None


def is_price_only(line: str) -> bool:
    return bool(_PAT_PRICE_ONLY.match(line.strip()))
