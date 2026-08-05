from __future__ import annotations

from collections.abc import Callable, Set
from dataclasses import dataclass
from typing import Literal

from ..constants import (
    ED_STEM_MIN_LENGTH,
    ED_SUFFIX_KEEP,
    EXCLUDED_SUFFIXES,
    NOUN_SUFFIX_KEEP,
    UN_PREFIX_KEEP,
    WHITELIST,
)

Kind = Literal['prefix', 'suffix']


@dataclass(frozen=True)
class Derivation:
    kind: Kind
    affix: str
    keep: frozenset[str] = frozenset()
    min_len: int = 0
    variants: Callable[[str], tuple[str, ...]] | None = None


def _ed_variants(stem: str) -> tuple[str, ...]:
    variants = [stem]
    # Why: "lipped" -> "lip" — final consonant doubles before -ed.
    if len(stem) > 2 and stem[-1] == stem[-2]:
        variants.append(stem[:-1])
    # Why: "nosed" -> "nose" — silent-e dropped before -ed.
    variants.append(stem + 'e')
    return tuple(variants)


def _ly_variants(stem: str) -> tuple[str, ...]:
    # Why: "happily" -> "happy" — -y rewrites to -i before -ly.
    # Why: "surely" -> "sure" — silent-e kept before -ly.
    return (stem, stem + 'i', stem + 'e')


DERIVATIONS: tuple[Derivation, ...] = (
    # Suffix/prefix stem rules strip mechanical transforms of a base word
    # (-ed/-ist/-ism/-ology/-ion/-ly, un-); the keep-lists rescue intentional forms.
    Derivation(kind='prefix', affix='un', keep=frozenset(UN_PREFIX_KEEP)),
    Derivation(
        kind='suffix',
        affix='ed',
        keep=frozenset(ED_SUFFIX_KEEP),
        min_len=ED_STEM_MIN_LENGTH,
        variants=_ed_variants,
    ),
    Derivation(kind='suffix', affix='ist', keep=frozenset(NOUN_SUFFIX_KEEP)),
    Derivation(kind='suffix', affix='ism', keep=frozenset(NOUN_SUFFIX_KEEP)),
    Derivation(kind='suffix', affix='ology', keep=frozenset(NOUN_SUFFIX_KEEP)),
    Derivation(kind='suffix', affix='ion', keep=frozenset(NOUN_SUFFIX_KEEP)),
    Derivation(kind='suffix', affix='ly', variants=_ly_variants),
)


def has_redundant_derivation(lemma: str, raw_word_set: Set[str]) -> bool:
    if lemma in WHITELIST:
        return False
    if any(lemma.endswith(suf) for suf in EXCLUDED_SUFFIXES):
        return True
    for derivation in DERIVATIONS:
        if derivation.kind == 'prefix':
            if not lemma.startswith(derivation.affix):
                continue
            if lemma in derivation.keep:
                continue
            if lemma[len(derivation.affix) :] in raw_word_set:
                return True
        else:
            if not lemma.endswith(derivation.affix):
                continue
            if lemma in derivation.keep:
                continue
            if len(lemma) < derivation.min_len:
                continue
            if derivation.variants is None:
                return True
            stem = lemma[: -len(derivation.affix)]
            if any(variant in raw_word_set for variant in derivation.variants(stem)):
                return True
    return False
