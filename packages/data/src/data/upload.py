#!/usr/bin/env python3
"""Upload today's generated words to MongoDB."""

from __future__ import annotations

import asyncio

from loguru import logger

from config.logger import setup_logging
from data.db import connect, disconnect
from data.repository import upload_words_for_day


def _async_main() -> int:
    setup_logging(name='data-upload')
    logger.info('Starting word upload to MongoDB')

    async def _run() -> int:
        await connect()
        try:
            result = await upload_words_for_day()
            logger.info(
                'Upload complete: {} inserted, {} updated, {} total',
                result['inserted'],
                result['updated'],
                result['total'],
            )
            return 0
        except Exception as exc:
            logger.exception('Upload failed: {}', exc)
            return 1
        finally:
            await disconnect()

    return asyncio.run(_run())


if __name__ == '__main__':
    raise SystemExit(_async_main())