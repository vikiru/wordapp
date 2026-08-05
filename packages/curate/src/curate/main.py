"""Curation pipeline entrypoint: prefilter the raw dictionary, keep every word
that survives the rejection gates, and write `filtered_words.txt`."""

from __future__ import annotations

import time
from pathlib import Path

import pycountry
from english_words import get_english_words_set
from loguru import logger

from config.logger import setup_logging
from curate.constants import CACHE_FILE, MAX_WORD_LENGTH, MIN_WORD_LENGTH, WHITELIST
from curate.utils import WordRecord, keep_base_lemma

setup_logging(name='curate')

COUNTRY_NAMES = {country.name.lower() for country in pycountry.countries}

CACHE_PATH = Path(CACHE_FILE)
OUT_PATH = Path('filtered_words.txt')


def prefilter(raw_words: set[str]) -> list[str]:
    """Keep whitelist entries; otherwise lowercase alpha words in the length window."""
    return [
        w.lower()
        for w in raw_words
        if w
        and (
            w.lower() in WHITELIST
            or (
                w.islower()
                and w.isalpha()
                and not any(c.isdigit() for c in w)
                and MIN_WORD_LENGTH <= len(w) <= MAX_WORD_LENGTH
                and w.lower() not in COUNTRY_NAMES
            )
        )
    ]


def keep_words(candidates: list[str], cache: dict[str, WordRecord], raw_word_set: set[str]) -> set[str]:
    """Return the base forms that survive every rejection gate."""
    kept: set[str] = set()
    total = len(candidates)
    start = time.perf_counter()
    for index, word in enumerate(candidates, 1):
        base_lemma = keep_base_lemma(word, cache, raw_word_set)
        if base_lemma is not None:
            kept.add(base_lemma)
        if index % 10_000 == 0 or index == total:
            elapsed = time.perf_counter() - start
            rate = index / elapsed if elapsed else 0.0
            eta = (total - index) / rate if rate else 0.0
            logger.info('Processed {:,}/{:,} words ({:.0f}/s, ETA {:.1f}s)', index, total, rate, eta)
    return kept


def write_filtered_words(words: set[str], out_path: Path) -> None:
    out_path.write_text(''.join(f'{word}\n' for word in sorted(words)), encoding='utf-8')
    logger.info('Wrote {:,} words to {}.', len(words), out_path)


def main() -> None:
    start_time = time.perf_counter()

    if not CACHE_PATH.exists():
        logger.warning('Cache {} is missing; building it first.', CACHE_PATH)
        from curate.build_cache import build_full_cached_metadata

        build_full_cached_metadata()

    cache = WordRecord.from_cache(CACHE_PATH.read_bytes())
    logger.info('Loaded metadata cache for {:,} words.', len(cache))

    raw_words = get_english_words_set(['web2'], lower=False)
    raw_word_set = {w.lower() for w in raw_words}

    logger.info('Prefiltering {:,} raw entries...', len(raw_words))
    candidates = prefilter(raw_words)
    logger.info('Retained {:,} shape-eligible candidates.', len(candidates))

    logger.info('Applying rejection gates to {:,} candidates...', len(candidates))
    curated_set = keep_words(candidates, cache, raw_word_set)
    logger.info('Kept {:,} words after curation.', len(curated_set))

    write_filtered_words(curated_set, OUT_PATH)
    logger.info('Finished in {:.2f}s.', time.perf_counter() - start_time)


if __name__ == '__main__':
    main()
