"""Repository layer for word persistence operations."""

from __future__ import annotations

from datetime import date

from pymongo import ReplaceOne

from data.models import WordDocument
from data.utils.io import load_generated_words, resolve_generation_date


async def upload_words_for_day(
    generation_date: date | None = None,
) -> dict[str, int]:
    """Load today's generated words and upsert them into MongoDB.

    Args:
        generation_date: Optional explicit date. If omitted, uses metadata date.

    Returns:
        Dict with counts: {"inserted": N, "updated": N, "total": N}
    """
    date_to_use = resolve_generation_date(generation_date)
    words = load_generated_words()

    if not words:
        return {'inserted': 0, 'updated': 0, 'total': 0}

    docs = [WordDocument.from_payload(w, date_to_use) for w in words]

    # Bulk upsert using ReplaceOne with upsert=True per word
    operations = [
        ReplaceOne(
            filter={'word': doc.word},
            replacement=doc.model_dump(mode='json'),
            upsert=True,
        )
        for doc in docs
    ]

    collection = WordDocument.get_pymongo_collection()
    result = await collection.bulk_write(operations, ordered=False)

    inserted = result.upserted_count
    updated = result.modified_count

    return {
        'inserted': inserted,
        'updated': updated,
        'total': len(docs),
    }


async def fetch_all_words() -> list[WordDocument]:
    """Fetch all persisted words from MongoDB."""
    return await WordDocument.find_all().to_list()


async def get_word(word: str) -> WordDocument | None:
    """Fetch a single word by its word field."""
    return await WordDocument.find_one(WordDocument.word == word)
