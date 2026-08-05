"""MongoDB connection management for the data package."""

from __future__ import annotations

from typing import Any

from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

from data.models import WordDocument
from data.utils.config import settings


def _db_name_from_uri(uri: str) -> str:
    """Extract database name from MongoDB URI, or return default."""
    try:
        parsed = parse_uri(uri)
        return parsed.get('database') or 'wordapp'
    except Exception:
        return 'wordapp'


_client: AsyncMongoClient[dict[str, Any]] | None = None


async def connect() -> AsyncMongoClient[dict[str, Any]]:
    """Initialize MongoDB connection and Beanie ODM."""
    global _client
    if _client is not None:
        return _client

    _client = AsyncMongoClient(settings.mongodb_uri)
    db_name = _db_name_from_uri(settings.mongodb_uri)
    db = _client[db_name]

    await init_beanie(
        database=db,
        document_models=[WordDocument],
    )
    return _client


async def disconnect() -> None:
    """Close MongoDB connection."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
