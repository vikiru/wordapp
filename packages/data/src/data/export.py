#!/usr/bin/env python3
"""Export all words from MongoDB to frontend data files."""

from __future__ import annotations

import asyncio

from loguru import logger

from config.logger import setup_logging
from data.db import connect, disconnect
from data.repository import fetch_all_words
from data.utils.io import resolve_generation_date, write_words_json, write_wotd_json


def _async_main() -> int:
    setup_logging(name='data-export')
    logger.info('Starting word export to frontend')

    async def _run() -> int:
        await connect()
        try:
            words = await fetch_all_words()
            if not words:
                logger.warning('No words found in database')
                return 0

            payload = [w.model_dump(mode='json') for w in words]

            # Write words.json (all words)
            write_words_json(payload)
            logger.info('Exported {} words to frontend/src/data/words.json', len(payload))

            # Write wotd.json (today's words based on latest generation_date)
            generation_date = resolve_generation_date()
            wotd_words = [w for w in payload if w.get('generation_date') == generation_date.isoformat()]
            write_wotd_json(wotd_words)
            logger.info('Exported {} words to frontend/src/data/wotd.json (date: {})', len(wotd_words), generation_date)

            return 0
        except Exception as exc:
            logger.exception('Export failed: {}', exc)
            return 1
        finally:
            await disconnect()

    return asyncio.run(_run())


if __name__ == '__main__':
    raise SystemExit(_async_main())