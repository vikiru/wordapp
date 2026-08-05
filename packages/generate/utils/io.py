from __future__ import annotations

from datetime import UTC, datetime

import orjson

from config import workspace_root
from models import GeneratedMetadata, GeneratedWord

GENERATE_DIR = workspace_root() / 'generate'
CURATE_DIR = workspace_root() / 'curate'

FILTERED_WORDS_FILE = CURATE_DIR / 'filtered_words.txt'
GENERATED_WORDS_FILE = GENERATE_DIR / 'generated_words.txt'
GENERATED_DATA_FILE = GENERATE_DIR / 'generated_data.json'
GENERATION_METADATA_FILE = GENERATE_DIR / 'generation_metadata.json'


def load_curated_words() -> list[str]:
    words = FILTERED_WORDS_FILE.read_text().strip().splitlines()
    return [word.strip().lower() for word in words if word.strip()]


def load_generated_words() -> set[str]:
    if not GENERATED_WORDS_FILE.exists():
        return set()
    words = GENERATED_WORDS_FILE.read_text().strip().splitlines()
    return {word.strip().lower() for word in words if word.strip()}


def write_outputs(
    entries: list[GeneratedWord],
    words: list[str],
    curated_count: int,
    remaining: int,
) -> None:
    GENERATED_DATA_FILE.write_bytes(orjson.dumps([entry.model_dump() for entry in entries]))

    with GENERATED_WORDS_FILE.open('a', encoding='utf-8') as fh:
        for word in words:
            fh.write(f'{word}\n')

    metadata = GeneratedMetadata(
        last_generation_date=datetime.now(UTC).strftime('%Y-%m-%d'),
        total_generated_words=len(load_generated_words()),
        total_curated_words=curated_count,
        words_generated_this_run=len(entries),
        remaining_words=remaining,
    )
    GENERATION_METADATA_FILE.write_bytes(orjson.dumps(metadata.model_dump(), option=orjson.OPT_INDENT_2))
