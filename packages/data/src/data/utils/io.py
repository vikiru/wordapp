"""I/O utilities for the data package."""

from __future__ import annotations

from datetime import date
from typing import Any

import orjson

from config import workspace_root
from data.utils.config import settings  # noqa: F401 - ensures env is loaded

GENERATE_DIR = workspace_root() / 'generate'
FRONTEND_DATA_DIR = workspace_root().parent / 'frontend' / 'src' / 'data'

GENERATED_DATA_FILE = GENERATE_DIR / 'generated_data.json'
GENERATION_METADATA_FILE = GENERATE_DIR / 'generation_metadata.json'
WORDS_JSON_FILE = FRONTEND_DATA_DIR / 'words.json'
WOTD_JSON_FILE = FRONTEND_DATA_DIR / 'wotd.json'
WORDS_TODAY_JSON_FILE = FRONTEND_DATA_DIR / 'words_today.json'
ARCHIVE_JSON_FILE = FRONTEND_DATA_DIR / 'archive.json'


def load_generated_words() -> list[dict[str, Any]]:
    """Load the latest generated words from the generate package output."""
    if not GENERATED_DATA_FILE.exists():
        raise FileNotFoundError(f'Generated data file not found: {GENERATED_DATA_FILE}')
    return orjson.loads(GENERATED_DATA_FILE.read_bytes())


def load_generation_metadata() -> dict[str, Any]:
    """Load generation metadata for date resolution."""
    if not GENERATION_METADATA_FILE.exists():
        raise FileNotFoundError(f'Generation metadata file not found: {GENERATION_METADATA_FILE}')
    return orjson.loads(GENERATION_METADATA_FILE.read_bytes())


def resolve_generation_date(explicit_date: date | None = None) -> date:
    """Resolve the generation date from explicit arg or metadata."""
    if explicit_date is not None:
        return explicit_date
    meta = load_generation_metadata()
    date_str = meta.get('last_generation_date')
    if not date_str:
        raise ValueError('No last_generation_date in metadata and no explicit date provided')
    return date.fromisoformat(str(date_str))


def write_words_json(words: list[dict[str, Any]]) -> None:
    """Write all words to frontend/src/data/words.json."""
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    WORDS_JSON_FILE.write_bytes(orjson.dumps(words))


def write_words_today_json(words: list[dict[str, Any]]) -> None:
    """Write the latest generation day's words to frontend/src/data/words_today.json."""
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    WORDS_TODAY_JSON_FILE.write_bytes(orjson.dumps(words))


def write_wotd_json(word: dict[str, Any]) -> None:
    """Write the day's featured word as a one-entry array to frontend/src/data/wotd.json."""
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    WOTD_JSON_FILE.write_bytes(orjson.dumps([word]))


def write_archive_json(days: dict[str, list[dict[str, Any]]]) -> None:
    """Write all words grouped by generation date to frontend/src/data/archive.json.

    Keys are ISO dates in the order provided (newest first by convention); each
    value is that day's full word documents.
    """
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_JSON_FILE.write_bytes(orjson.dumps(days))


def get_wotd_from_db(generation_date: date) -> list[dict[str, Any]]:
    """Fetch words for a specific generation date directly from the database."""
    # This is a sync wrapper for the CLI use case
    import asyncio

    from data.db import connect, disconnect
    from data.models import WordDocument

    async def _fetch() -> list[dict[str, Any]]:
        await connect()
        try:
            words = await WordDocument.find(WordDocument.generation_date == generation_date.isoformat()).to_list()
            return [w.model_dump(mode='json') for w in words]
        finally:
            await disconnect()

    return asyncio.run(_fetch())
