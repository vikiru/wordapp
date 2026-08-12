from __future__ import annotations

import argparse
import os
import sys
from datetime import date

from loguru import logger

from config import load_env
from config.logger import setup_logging
from generate.utils import (
    build_client,
    generate_entries,
    load_curated_words,
    load_generated_words,
    log_run_summary,
    parse_mmddyyyy,
    select_words,
    write_outputs,
)

DEFAULT_MODEL = 'gemini-3.1-flash-lite'


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='generate',
        description='Generate words for today or a specific date (MM/DD/YYYY).',
    )
    parser.add_argument(
        'date',
        nargs='?',
        metavar='MM/DD/YYYY',
        help='target generation date, e.g. 08/09/2026 (default: today)',
    )
    return parser.parse_args(argv)


def _resolve_date(value: str | None) -> date:
    if value is None:
        return date.today()
    try:
        return parse_mmddyyyy(value)
    except ValueError:
        logger.error(
            'generate: Invalid date {!r}. Expected MM/DD/YYYY (e.g. 08/09/2026).',
            value,
        )
        sys.exit(1)


def main() -> None:
    load_env()
    setup_logging(name='generate')

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error('generate: GEMINI_API_KEY environment variable is required.')
        sys.exit(1)

    model = os.environ.get('GEMINI_MODEL', DEFAULT_MODEL)
    target_date = _resolve_date(_parse_args(sys.argv[1:]).date)

    curated = load_curated_words()
    generated = load_generated_words()
    logger.info(
        'generate: Loaded {} curated words, {} already generated. Target date: {}.',
        len(curated),
        len(generated),
        target_date,
    )

    words = select_words(curated, generated)
    if not words:
        logger.info('generate: Pool exhausted; writing empty run metadata.')
        write_outputs(
            entries=[],
            words=[],
            curated_count=len(curated),
            remaining=0,
            generation_date=target_date,
            model=model,
        )
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
        generation_date=target_date,
        model=model,
    )

    log_run_summary(
        generated_count=generated_count,
        failed_count=failed_count,
        remaining=remaining,
    )


if __name__ == '__main__':
    main()
