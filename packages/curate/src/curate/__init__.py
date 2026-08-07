"""Curate package for word curation pipeline."""

from curate.constants import (
    CACHE_FILE,
    EXCLUDED_WORDS,
    MAX_WORD_LENGTH,
    MIN_WORD_LENGTH,
    WHITELIST,
)
from curate.models import WordRecord
from curate.utils import (
    has_redundant_derivation,
    keep_base_lemma,
    resolve_base_lemma,
)

__all__ = [
    'CACHE_FILE',
    'EXCLUDED_WORDS',
    'MAX_WORD_LENGTH',
    'MIN_WORD_LENGTH',
    'WHITELIST',
    'WordRecord',
    'has_redundant_derivation',
    'keep_base_lemma',
    'resolve_base_lemma',
]
