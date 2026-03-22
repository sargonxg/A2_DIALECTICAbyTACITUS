"""
Temporal Normalization — Parse dates, durations, and sequences.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

# Common date patterns
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_MONTH_YEAR = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
    re.IGNORECASE,
)
_RELATIVE = re.compile(
    r"(\d+)\s+(days?|weeks?|months?|years?)\s+(ago|later|before|after)", re.IGNORECASE
)

_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_date(text: str, reference_date: datetime | None = None) -> datetime | None:
    """Attempt to parse a date from text.

    Handles: ISO dates, "Month Year", relative dates.
    Returns None if parsing fails.
    """
    text = text.strip()

    # Try ISO format
    match = _ISO_DATE.search(text)
    if match:
        try:
            return datetime.fromisoformat(match.group())
        except ValueError:
            pass

    # Try Month Year
    match = _MONTH_YEAR.search(text)
    if match:
        month = _MONTHS.get(match.group(1).lower())
        year = int(match.group(2))
        if month:
            return datetime(year, month, 1)

    # Try relative date
    ref = reference_date or datetime.utcnow()
    match = _RELATIVE.search(text)
    if match:
        num = int(match.group(1))
        unit = match.group(2).lower().rstrip("s")
        direction = match.group(3).lower()
        delta = _unit_to_timedelta(num, unit)
        if direction in ("ago", "before"):
            return ref - delta
        else:
            return ref + delta

    return None


def _unit_to_timedelta(num: int, unit: str) -> timedelta:
    if unit == "day":
        return timedelta(days=num)
    elif unit == "week":
        return timedelta(weeks=num)
    elif unit == "month":
        return timedelta(days=num * 30)
    elif unit == "year":
        return timedelta(days=num * 365)
    return timedelta()


def extract_temporal_sequence(texts: list[str]) -> list[tuple[str, datetime | None]]:
    """Extract and order temporal references from a list of text passages."""
    results = []
    for text in texts:
        dt = parse_date(text)
        results.append((text, dt))
    # Sort by date (None dates at end)
    results.sort(key=lambda x: (x[1] is None, x[1] or datetime.max))
    return results
