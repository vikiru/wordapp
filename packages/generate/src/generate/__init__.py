"""Top-level `generate` namespace.

The generate package uses a flat layout (top-level `models`, `prompts`,
`utils` modules). This module gives it a proper importable namespace so other
workspace packages can import it unambiguously as `generate` (e.g.
`from generate import GeneratedWord`) instead of the bare `models` module.
"""

from generate.models.word_entry import (
    Etymology,
    GeneratedMetadata,
    GeneratedWord,
    Inflections,
    PartOfSpeech,
    Pronunciation,
    WordForm,
    WordRelation,
    WordSense,
)

__all__ = [
    'Etymology',
    'GeneratedMetadata',
    'GeneratedWord',
    'Inflections',
    'PartOfSpeech',
    'Pronunciation',
    'WordForm',
    'WordRelation',
    'WordSense',
]
