from __future__ import annotations

import re

_SWAP_PATTERNS = [
    re.compile(r"\bswap(?:ping)?\b", re.IGNORECASE),
    re.compile(r"\bexchange\b", re.IGNORECASE),
    re.compile(r"\btrade\b", re.IGNORECASE),
]

_SELL_PATTERNS = [
    re.compile(r"\bwts\b", re.IGNORECASE),
    re.compile(r"\bsell(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\btransfer\b", re.IGNORECASE),
    re.compile(r"\blet(?:ting)?\s+go\b", re.IGNORECASE),
    re.compile(r"\bto\s+let\s+go\b", re.IGNORECASE),
    re.compile(r"\bat\s+cost\b", re.IGNORECASE),
]

_BUY_PATTERNS = [
    re.compile(r"\bwtb\b", re.IGNORECASE),
    re.compile(r"\bbuy(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\blooking\s+for\b", re.IGNORECASE),
    re.compile(r"\bfind\b", re.IGNORECASE),
    re.compile(r"\blf\b", re.IGNORECASE),
    re.compile(r"\bneed(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\bwanted?\b", re.IGNORECASE),
    re.compile(r"\bseeking\b", re.IGNORECASE),
]


def _classify(text: str) -> str | None:
    if any(p.search(text) for p in _SWAP_PATTERNS):
        return "swap"
    if any(p.search(text) for p in _SELL_PATTERNS):
        return "sell"
    if any(p.search(text) for p in _BUY_PATTERNS):
        return "buy"
    return None


def detect_intent(text: str) -> str:
    """Return 'swap', 'sell', 'buy', or 'unknown' for the primary intent in text.

    Intent is read from the first 3 non-empty lines so that footer mentions of
    swap/buy (e.g. "will prioritise users who want to swap") don't override the
    primary intent stated in the message header.
    """
    header_lines = [ln for ln in text.splitlines() if ln.strip()][:3]
    header = "\n".join(header_lines)
    result = _classify(header)
    if result is not None:
        return result
    # Fall back to full text if the header didn't match anything
    return _classify(text) or "unknown"
