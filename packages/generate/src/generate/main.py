from __future__ import annotations

import os
import sys

from loguru import logger

from config import load_env
from config.logger import setup_logging
from generate.utils import (
    build_client,
    generate_entries,
    load_curated_words,
    load_generated_words,
    log_run_summary,
    select_words,
    write_outputs,
)

DEFAULT_MODEL = 'gemini-3.1-flash-lite'


def main() -> None:
    load_env()
    setup_logging(name='generate')

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error('generate: GEMINI_API_KEY environment variable is required.')
        sys.exit(1)

    model = os.environ.get('GEMINI_MODEL', DEFAULT_MODEL)

    curated = load_curated_words()
    generated = load_generated_words()
    logger.info(
        'generate: Loaded {} curated words, {} already generated.',
        len(curated),
        len(generated),
    )

    words = select_words(curated, generated)
    if not words:
        return

    client = build_client(api_key=api_key)
    logger.info('generate: Generating entries for {} words with model {}.', len(words), model)

    try:
        entries = generate_entries(client, model, words)
    except Exception as exc:
        logger.error('generate: Failed to generate entries: {}.', exc)
        sys.exit(1)

    generated_count = len(entries)
    failed_count = len(words) - generated_count
    remaining = len(curated) - len(generated) - generated_count

    write_outputs(
        entries=entries,
        words=[entry.word for entry in entries],
        curated_count=len(curated),
        remaining=remaining,
    )

    log_run_summary(
        generated_count=generated_count,
        failed_count=failed_count,
        remaining=remaining,
    )


if __name__ == '__main__':
    main()
