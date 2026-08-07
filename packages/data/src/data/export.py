#!/usr/bin/env python3
"""Export all words from MongoDB to frontend data files."""

from __future__ import annotations

import asyncio

from loguru import logger

from config.logger import setup_logging
from data.db import connect, disconnect
from data.models import ArchiveFile, WordsFile, WordsTodayFile, WotdFile
from data.repository import fetch_all_words, fetch_words_grouped_by_date
from data.utils.io import (
    write_archive_json,
    write_words_json,
    write_words_today_json,
    write_wotd_json,
)


def _async_main() -> int:
    setup_logging(name='data-export')

    async def _run() -> int:
        await connect()
        try:
            grouped = await fetch_words_grouped_by_date()
            if not grouped:
                logger.warning('data: No words found in database.')
                return 0

            all_words = await fetch_all_words()

            payload = {
                iso_date: [w.model_dump(mode='json') for w in words]
                for iso_date, words in grouped.items()
            }
            ArchiveFile.model_validate(payload)
            words_payload = [w.model_dump(mode='json') for w in all_words]
            WordsFile.model_validate(words_payload)

            # Write words.json (all words, A-Z; alphabetical order from the query)
            write_words_json(words_payload)
            logger.info('data: Exported {} words to frontend/src/data/words.json.', len(words_payload))

            # Write archive.json (all words grouped by generation date)
            write_archive_json(payload)
            logger.info('data: Exported {} days to frontend/src/data/archive.json.', len(payload))

            # Write the daily files: words_today.json (the latest generation
            # day's words) and wotd.json (the day's featured word — the entry
            # flagged is_wotd, else the day's first entry).
            latest_date = max(payload)
            words_today = payload[latest_date]
            featured = next((w for w in words_today if w.get('is_wotd')), words_today[0])
            WordsTodayFile.model_validate(words_today)
            WotdFile.model_validate(featured)
            write_words_today_json(words_today)
            logger.info(
                'data: Exported {} words to frontend/src/data/words_today.json (date: {}).',
                len(words_today),
                latest_date,
            )
            write_wotd_json(featured)
            logger.info(
                'data: Exported featured word to frontend/src/data/wotd.json (word: {}).',
                featured['word'],
            )

            return 0
        except Exception as exc:
            logger.exception('data: Export failed: {}.', exc)
            return 1
        finally:
            await disconnect()

    return asyncio.run(_run())


if __name__ == '__main__':
    raise SystemExit(_async_main())