from __future__ import annotations

import random

from google import genai
from google.genai import types
from loguru import logger

from models import GeneratedWord
from prompts import SYSTEM_PROMPT
from utils.schema import build_response_schema

DEFAULT_MODEL = 'gemini-3.1-flash-lite'

TEXT_HARM_CATEGORIES = (
    types.HarmCategory.HARM_CATEGORY_HARASSMENT,
    types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
)

MAX_SAFETY_SETTINGS = [
    types.SafetySetting(
        category=category,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    )
    for category in TEXT_HARM_CATEGORIES
]


def select_random_wotd(entries: list[GeneratedWord]) -> list[GeneratedWord]:
    """Randomly select one word as WOTD from the given entries.

    Sets is_wotd=True for the selected word, False for all others.
    """
    if not entries:
        return entries

    wotd_index = random.randrange(len(entries))
    for i, entry in enumerate(entries):
        entry.is_wotd = (i == wotd_index)

    logger.info(f'Randomly selected WOTD: {entries[wotd_index].word}')
    return entries


def ensure_single_wotd(entries: list[GeneratedWord]) -> list[GeneratedWord]:
    """Validate and enforce exactly one WOTD in the entries.

    - If AI marked exactly one: keep it
    - If AI marked none: randomly select one
    - If AI marked multiple: keep the first one, clear the rest
    """
    if not entries:
        return entries

    wotd_count = sum(1 for e in entries if e.is_wotd)

    if wotd_count == 0:
        # No WOTD selected by AI, randomly select one
        return select_random_wotd(entries)
    elif wotd_count > 1:
        # Multiple WOTDs selected, keep only the first one
        logger.warning('Multiple words marked as WOTD by AI, keeping only the first')
        seen_first = False
        for entry in entries:
            if entry.is_wotd:
                if not seen_first:
                    seen_first = True
                else:
                    entry.is_wotd = False

    return entries


def generate_entries(client: genai.Client, model: str, words: list[str]) -> list[GeneratedWord]:
    words_list = '\n'.join(f'- {word}' for word in words)
    contents = f'{SYSTEM_PROMPT}\n\nGenerate entries for the following words:\n{words_list}'
    config = types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=build_response_schema(),
        temperature=0.3,
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # 0 = disable thinking
        safety_settings=MAX_SAFETY_SETTINGS,
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    parsed = response.parsed
    if parsed is None:
        raise ValueError('Gemini returned no parseable content')
    entries = parsed if isinstance(parsed, list) else [parsed]
    if not entries:
        raise ValueError('Gemini returned an empty entry list')
    validated = []
    for i, entry in enumerate(entries):
        try:
            validated.append(GeneratedWord.model_validate(entry))
        except Exception as exc:  # noqa: BLE001 - invalid entry for a word
            word = words[i] if i < len(words) else f'entry-{i}'
            logger.error(f'Failed to validate entry for {word}: {exc}')

    # Validate WOTD selection: ensure exactly one word has is_wotd=True
    return ensure_single_wotd(validated)


def build_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def log_run_summary(generated_count: int, failed_count: int, remaining: int) -> None:
    logger.info(f'Summary: {generated_count} generated, {failed_count} failed, {remaining} remaining')