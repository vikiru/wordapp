"""Beanie ODM documents for generated words."""

from __future__ import annotations

from datetime import date
from typing import Any

from beanie import Document
from pydantic import BaseModel, Field, field_serializer
from pymongo import IndexModel


class PronunciationDoc(BaseModel):
    """Embedded pronunciation document."""

    ipa: str | None = None
    phonetic: str | None = None


class EtymologyDoc(BaseModel):
    """Embedded etymology document."""

    origin_language: str | None = None
    original_word: str | None = None
    first_recorded: str | None = None
    explanation: str | None = None


class WordSenseDoc(BaseModel):
    """Embedded word sense document."""

    part_of_speech: str
    definition: str
    examples: list[str] = Field(min_length=1, max_length=3)
    usage_notes: list[str] = []


class WordRelationDoc(BaseModel):
    """Embedded word relation (synonym/antonym) document."""

    word: str
    part_of_speech: str
    differentiator: str | None = None


class WordFormDoc(BaseModel):
    """Embedded word family form document."""

    word: str
    part_of_speech: str | None = None
    ipa: str | None = None


class InflectionsDoc(BaseModel):
    """Embedded inflections document."""

    past: str | list[str] | None = None
    past_participle: str | list[str] | None = None
    present_participle: str | list[str] | None = None
    plural: str | list[str] | None = None
    comparative: str | list[str] | None = None
    superlative: str | list[str] | None = None

    @field_serializer('past', 'past_participle', 'present_participle', 'plural', 'comparative', 'superlative')
    def _flatten_to_string(self, v: str | list[str] | None) -> str | None:
        if isinstance(v, list):
            return ', '.join(v)
        return v


class WordDocument(Document):
    """Beanie document for a generated word."""

    word: str
    pos_tags: list[str] = Field(min_length=1)
    senses: list[WordSenseDoc] = Field(min_length=1)
    synonyms: list[WordRelationDoc] = Field(max_length=4)
    antonyms: list[WordRelationDoc] = Field(max_length=4)
    inflections: InflectionsDoc | None = None
    word_family: list[WordFormDoc] = []
    pronunciation: PronunciationDoc
    etymology: list[EtymologyDoc] = []
    common_mistakes: list[str] = Field(max_length=3)
    interesting_fact: str | None = None
    is_wotd: bool = False
    past_wotd: bool = False
    generation_date: date

    class Settings:
        name = 'words'
        use_revision = False
        indexes = [
            IndexModel('word', unique=True),
            IndexModel([('generation_date', 1)]),
            IndexModel(
                [('is_wotd', 1)],
                unique=True,
                partialFilterExpression={'is_wotd': True},
            ),
        ]

    @classmethod
    def from_payload(cls, payload: dict[str, Any], generation_date: date) -> WordDocument:
        """Create a WordDocument from a GeneratedWord payload dict."""
        return cls(
            word=payload['word'],
            pos_tags=payload['pos_tags'],
            senses=[
                WordSenseDoc(
                    part_of_speech=s['part_of_speech'],
                    definition=s['definition'],
                    examples=s['examples'],
                    usage_notes=s.get('usage_notes', []),
                )
                for s in payload['senses']
            ],
            synonyms=[
                WordRelationDoc(
                    word=sr['word'],
                    part_of_speech=sr['part_of_speech'],
                    differentiator=sr.get('differentiator'),
                )
                for sr in payload.get('synonyms', [])
            ],
            antonyms=[
                WordRelationDoc(
                    word=sr['word'],
                    part_of_speech=sr['part_of_speech'],
                    differentiator=sr.get('differentiator'),
                )
                for sr in payload.get('antonyms', [])
            ],
            inflections=(
                InflectionsDoc(
                    past=payload['inflections'].get('past'),
                    past_participle=payload['inflections'].get('past_participle'),
                    present_participle=payload['inflections'].get('present_participle'),
                    plural=payload['inflections'].get('plural'),
                    comparative=payload['inflections'].get('comparative'),
                    superlative=payload['inflections'].get('superlative'),
                )
                if payload.get('inflections') is not None
                else None
            ),
            word_family=[
                WordFormDoc(
                    word=wf['word'],
                    part_of_speech=wf.get('part_of_speech'),
                    ipa=wf.get('ipa'),
                )
                for wf in payload.get('word_family', [])
            ],
            pronunciation=PronunciationDoc(
                ipa=payload['pronunciation']['ipa'],
                phonetic=payload['pronunciation']['phonetic'],
            ),
            etymology=[
                EtymologyDoc(
                    origin_language=e.get('origin_language'),
                    original_word=e.get('original_word'),
                    first_recorded=e.get('first_recorded'),
                    explanation=e.get('explanation'),
                )
                for e in payload.get('etymology', [])
            ],
            common_mistakes=payload.get('common_mistakes', []),
            interesting_fact=payload.get('interesting_fact'),
            is_wotd=payload.get('is_wotd', False),
            generation_date=generation_date,
        )
