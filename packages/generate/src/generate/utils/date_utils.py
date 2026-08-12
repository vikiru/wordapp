"""Date parsing helpers for targeting a generation run at a specific day."""

from __future__ import annotations

from datetime import date, datetime

DATE_FORMAT = '%m/%d/%Y'


def parse_mmddyyyy(value: str) -> date:
    """Parse a ``MM/DD/YYYY`` string into a date.

    Raises ValueError for malformed formats and impossible dates (e.g.
    02/30/2026); the caller surfaces the expected format in its error message.
    """
    return datetime.strptime(value, DATE_FORMAT).date()


def format_iso(value: date) -> str:
    """Format a date as ISO 8601 (``YYYY-MM-DD``)."""
    return value.isoformat()
