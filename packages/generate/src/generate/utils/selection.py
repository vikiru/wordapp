from __future__ import annotations

import random

from loguru import logger

WORDS_PER_RUN = 10


def select_words(curated: list[str], generated: set[str]) -> list[str]:
    available = [word for word in curated if word not in generated]
    if not available:
        logger.info('generate: No ungenerated words remain; nothing to do.')
        return []
    count = min(WORDS_PER_RUN, len(available))
    return random.sample(available, count)
