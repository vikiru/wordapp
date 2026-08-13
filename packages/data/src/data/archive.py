#!/usr/bin/env python3
"""Export all words grouped by generation date to frontend/src/data/archive.json."""

from __future__ import annotations

import asyncio

from loguru import logger

from config.logger import setup_logging
from data.db import connect, disconnect
from data.models import ArchiveFile
from data.repository import fetch_words_grouped_by_date
from data.utils.io import write_archive_json


def _async_main() -> int:
    setup_logging(name='data-archive')

    async def _run() -> int:
        await connect()
        try:
            grouped = await fetch_words_grouped_by_date()
            if not grouped:
                logger.warning('data: No words found in database.')
                return 0

            payload = {iso_date: [w.model_dump(mode='json') for w in words] for iso_date, words in grouped.items()}
            ArchiveFile.model_validate(payload)
            write_archive_json(payload)
            logger.info('data: Exported {} days to frontend/src/data/archive.json.', len(payload))
            return 0
        except Exception as exc:
            logger.exception('data: Archive export failed: {}.', exc)
            return 1
        finally:
            await disconnect()

    return asyncio.run(_run())


if __name__ == '__main__':
    raise SystemExit(_async_main())
