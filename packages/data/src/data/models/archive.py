"""Plain-pydantic models for `frontend/src/data/archive.json`.

An archive entry is a persisted word: the generate package's authoritative
`GeneratedWord` shape plus the persistence fields the data layer stamps
(`generation_date`, `id`). Subclassing keeps the file contract in sync with
`GeneratedWord` — no mirror to drift.

These models are Beanie-free on purpose: `WordDocument.model_validate` requires
an initialized Beanie connection (overridden `__init__`), while a static file
validator must validate JSON offline.
"""

from __future__ import annotations

from datetime import date

from pydantic import RootModel

from generate import GeneratedWord


class ArchiveEntry(GeneratedWord):
    """One word as persisted in `archive.json`: `GeneratedWord` + persistence fields."""

    generation_date: date
    id: str | None = None


class ArchiveFile(RootModel[dict[date, list[ArchiveEntry]]]):
    """`frontend/src/data/archive.json`: ISO generation date -> that day's entries.

    Keys are `date` objects parsed from ISO strings (rejected when not valid
    dates) and serialized back to ISO format; ordered newest-first. Validating
    an `ArchiveFile` validates every entry it contains.
    """


class WordsFile(RootModel[list[ArchiveEntry]]):
    """`frontend/src/data/words.json`: every persisted word, sorted A-Z.

    Entries are the same persisted shape as archive entries; the alphabetical
    order is guaranteed by the export query, not by this model.
    """


class WordsTodayFile(RootModel[list[ArchiveEntry]]):
    """`frontend/src/data/words_today.json`: the latest generation day's words."""


class WotdFile(RootModel[ArchiveEntry]):
    """`frontend/src/data/wotd.json`: the day's featured word.

    The entry flagged `is_wotd`, else the day's first entry.
    """
