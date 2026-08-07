"""Declarative rejection pipeline.

A word is kept only if it survives every gate in order. Raw gates inspect the
cache entry for the word itself; lemma gates inspect the entry for its resolved
base form. The whitelist bypasses every gate by design.

Add or remove a rule by editing one entry in RAW_GATES or LEMMA_GATES; the
entry name is the rejection reason used in audit output.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Set
from dataclasses import dataclass, field, replace

from wordfreq import zipf_frequency

from ..constants import (
    DEFINITION_ORIGIN_MARKERS,
    EXCLUDED_HYPERNYMS,
    EXCLUDED_RELATED_TARGETS,
    EXCLUDED_WORDS,
    MAX_WORD_LENGTH,
    MIN_WORD_LENGTH,
    NAMED_INSTANCE_CATEGORIES,
    TARGETED_LEAKS,
    TAXONOMY_ROOT_EXCLUSIONS,
    WHITELIST,
)
from ..models import WordRecord
from .derivations import has_redundant_derivation
from .lemmatize import resolve_base_lemma
from .zipf import within_zipf_window

_origin_marker = re.compile(DEFINITION_ORIGIN_MARKERS.pattern)


def _blank_record() -> WordRecord:
    """Cache-shaped record for words with no metadata entry."""
    return WordRecord(lemma='', is_profanity=False, has_wn=False, is_valid_wn=False, is_named_individual=False)


@dataclass(frozen=True)
class Context:
    """Everything a gate inspects; lemma fields fill in once the base form is resolved."""

    word: str
    record: WordRecord
    base_lemma: str = ''
    lemma_record: WordRecord = field(default_factory=_blank_record)
    raw_word_set: Set[str] = frozenset()


GateFn = Callable[[Context], bool]


@dataclass(frozen=True)
class Gate:
    """A single rejection rule; the name doubles as the rejection reason."""

    name: str
    applies: GateFn


def _g_origin_markers(ctx: Context) -> bool:
    """Definitions mention a foreign or culturally-specific origin."""
    return any(_origin_marker.search(definition) for definition in ctx.record.definitions)


def _g_excluded_hypernyms(ctx: Context) -> bool:
    return bool(ctx.record.direct_hypernyms & EXCLUDED_HYPERNYMS)


def _g_related_targets_raw(ctx: Context) -> bool:
    return bool(ctx.record.related_targets & EXCLUDED_RELATED_TARGETS)


def _g_excluded_word_raw(ctx: Context) -> bool:
    return ctx.word in EXCLUDED_WORDS


def _g_named_individual_raw(ctx: Context) -> bool:
    return ctx.record.is_named_individual


def _g_named_instance(ctx: Context) -> bool:
    return bool(ctx.record.instance_hypernyms & NAMED_INSTANCE_CATEGORIES)


def _g_taxonomy_root(ctx: Context) -> bool:
    return bool(ctx.record.roots & TAXONOMY_ROOT_EXCLUSIONS)


RAW_GATES: tuple[Gate, ...] = (
    Gate('origin_markers', _g_origin_markers),
    Gate('excluded_hypernyms', _g_excluded_hypernyms),
    Gate('excluded_related_targets', _g_related_targets_raw),
    Gate('excluded_words', _g_excluded_word_raw),
    Gate('named_individual', _g_named_individual_raw),
    Gate('named_instance_categories', _g_named_instance),
    Gate('taxonomy_root_exclusions', _g_taxonomy_root),
)


def _g_profanity(ctx: Context) -> bool:
    return ctx.lemma_record.is_profanity


def _g_named_individual_lemma(ctx: Context) -> bool:
    return ctx.lemma_record.is_named_individual


def _g_invalid_wn(ctx: Context) -> bool:
    return ctx.lemma_record.invalid_wn()


def _g_related_targets_lemma(ctx: Context) -> bool:
    return bool(ctx.lemma_record.related_targets & EXCLUDED_RELATED_TARGETS)


def _g_excluded_word_lemma(ctx: Context) -> bool:
    return ctx.base_lemma in EXCLUDED_WORDS


def _g_redundant_derivation(ctx: Context) -> bool:
    return has_redundant_derivation(ctx.base_lemma, ctx.raw_word_set)


def _g_targeted_leaks(ctx: Context) -> bool:
    return any(token in ctx.word or token in ctx.base_lemma for token in TARGETED_LEAKS)


def _g_zipf_window(ctx: Context) -> bool:
    # Cache carries zipf for known words; compute on the fly only when absent.
    raw_frequency = ctx.record.zipf if ctx.record.has_wn else zipf_frequency(ctx.word, 'en')
    lemma_frequency = zipf_frequency(ctx.base_lemma, 'en')
    return not within_zipf_window(raw_frequency, lemma_frequency)


def _g_has_wn(ctx: Context) -> bool:
    return not ctx.record.has_wn


LEMMA_GATES: tuple[Gate, ...] = (
    Gate('profanity', _g_profanity),
    Gate('named_individual', _g_named_individual_lemma),
    Gate('invalid_wn', _g_invalid_wn),
    Gate('excluded_related_targets', _g_related_targets_lemma),
    Gate('excluded_words', _g_excluded_word_lemma),
    Gate('redundant_derivation', _g_redundant_derivation),
    Gate('targeted_leaks', _g_targeted_leaks),
    Gate('zipf_window', _g_zipf_window),
    Gate('has_wn', _g_has_wn),
)


def _rejected(ctx: Context, gates: tuple[Gate, ...]) -> bool:
    return any(gate.applies(ctx) for gate in gates)


def keep_base_lemma(word: str, cache: dict[str, WordRecord], raw_word_set: set[str]) -> str | None:
    """Return the base form to keep, or None when any gate rejects the word."""
    if word in WHITELIST:
        return word

    ctx = Context(word=word, record=cache.get(word) or _blank_record(), raw_word_set=raw_word_set)
    if _rejected(ctx, RAW_GATES):
        return None

    base_lemma = resolve_base_lemma(word, ctx.record)
    if not base_lemma or not base_lemma.isalpha() or not (MIN_WORD_LENGTH <= len(base_lemma) <= MAX_WORD_LENGTH):
        return None

    ctx = replace(ctx, base_lemma=base_lemma, lemma_record=cache.get(base_lemma) or _blank_record())
    if _rejected(ctx, LEMMA_GATES):
        return None
    return base_lemma
