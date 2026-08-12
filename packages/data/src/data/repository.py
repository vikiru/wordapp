"""Repository layer for word persistence operations."""

from __future__ import annotations

from datetime import date

from beanie.odm.enums import SortDirection
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
        await clear_wotd()
        return {'inserted': 0, 'updated': 0, 'total': 0}

    docs = [WordDocument.from_payload(w, date_to_use) for w in words]
    existing = await WordDocument.find({'word': {'$in': [doc.word for doc in docs]}}).to_list()
    past_wotd_by_word = {doc.word: doc.past_wotd for doc in existing}
    for doc in docs:
        doc.is_wotd = False
        doc.past_wotd = past_wotd_by_word.get(doc.word, False)

    # Bulk upsert using ReplaceOne with upsert=True per word
    operations = [
        ReplaceOne(
            filter={'word': doc.word},
            replacement=doc.model_dump(mode='json', exclude={'id'}),
            upsert=True,
        )
        for doc in docs
    ]

    collection = WordDocument.get_pymongo_collection()
    result = await collection.bulk_write(operations, ordered=False)

    await replace_wotd(next((w['word'] for w in words if w.get('is_wotd')), docs[0].word))

    inserted = result.upserted_count
    updated = result.modified_count

    return {
        'inserted': inserted,
        'updated': updated,
        'total': len(docs),
    }


async def get_wotd() -> WordDocument | None:
    """Fetch the current Word of the Day (the single doc with ``is_wotd`` true)."""
    return await WordDocument.find_one({'is_wotd': True})


async def clear_wotd() -> None:
    """Demote the current Word of the Day (exhaustion path).

    The demoted WOTD is marked ``past_wotd`` so it stays queryable as a former
    Word of the Day after the live ``is_wotd`` flag moves on.
    """
    await WordDocument.get_pymongo_collection().update_many(
        {'is_wotd': True},
        {'$set': {'is_wotd': False, 'past_wotd': True}},
    )


async def replace_wotd(word: str) -> WordDocument | None:
    """Make ``word`` the Word of the Day, demoting any previous one.

    The current WOTD is cleared first (and marked ``past_wotd``) so the partial
    unique index never holds two documents with ``is_wotd: True`` at once.
    """
    await clear_wotd()
    doc = await get_word(word)
    if doc is None:
        return None
    doc.is_wotd = True
    await doc.save()
    return doc


async def fetch_all_words() -> list[WordDocument]:
    """Fetch all persisted words from MongoDB, sorted alphabetically (A-Z) by word.

    The sort is served by the unique ``word`` index.
    """
    return await WordDocument.find_all().sort(('word', SortDirection.ASCENDING)).to_list()


async def fetch_words_grouped_by_date() -> dict[str, list[WordDocument]]:
    """Fetch all words grouped by generation date.

    Returns a mapping of ISO date string to that day's documents, dates sorted
    newest first. Grouping happens in Python over a date-sorted scan: at ~10
    words/day a ``$group`` aggregation would only add BSON-to-JSON conversion
    without saving anything.
    """
    all_words = await WordDocument.find_all().sort(('generation_date', SortDirection.DESCENDING)).to_list()
    grouped: dict[str, list[WordDocument]] = {}
    for doc in all_words:
        grouped.setdefault(doc.generation_date.isoformat(), []).append(doc)
    return grouped


async def get_word(word: str) -> WordDocument | None:
    """Fetch a single word by its word field."""
    return await WordDocument.find_one(WordDocument.word == word)
