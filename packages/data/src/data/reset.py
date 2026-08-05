#!/usr/bin/env python3
"""Reset all word documents from MongoDB."""

from __future__ import annotations

import asyncio

from loguru import logger

from config.logger import setup_logging
from data.db import connect, disconnect
from data.models import WordDocument


def _async_main() -> int:
    setup_logging(name='data-reset')
    logger.info('Starting data reset')

    async def _run() -> int:
        await connect()
        try:
            collection = WordDocument.get_pymongo_collection()
            result = await collection.delete_many({})
            deleted_count = result.deleted_count
            logger.info('Deleted {} word documents from MongoDB', deleted_count)
            return 0
        except Exception as exc:
            logger.exception('Reset failed: {}', exc)
            return 1
        finally:
            await disconnect()

    return asyncio.run(_run())


if __name__ == '__main__':
    raise SystemExit(_async_main())