from __future__ import annotations

from simplemma import Lemmatizer
from simplemma.strategies import DefaultStrategy

from ..constants import SPELLING_VARIANTS
from ..models import WordRecord

lemmatizer = Lemmatizer(cache_max_size=16, lemmatization_strategy=DefaultStrategy())


def resolve_base_lemma(word: str, wn_record: WordRecord) -> str:
    lemma = (wn_record.lemma or lemmatizer.lemmatize(word, 'en')).lower()
    return SPELLING_VARIANTS.get(lemma, lemma)
