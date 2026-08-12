from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_serializer, field_validator


class PartOfSpeech(StrEnum):
    noun = 'noun'
    verb = 'verb'
    adjective = 'adjective'
    adverb = 'adverb'
    pronoun = 'pronoun'
    preposition = 'preposition'
    conjunction = 'conjunction'
    interjection = 'interjection'
    determiner = 'determiner'


class Pronunciation(BaseModel):
    ipa: str | None = None
    phonetic: str | None = None


class Etymology(BaseModel):
    origin_language: str | None = None
    original_word: str | None = None
    first_recorded: str | None = None
    explanation: str | None = None


class WordSense(BaseModel):
    part_of_speech: PartOfSpeech
    definition: str
    examples: list[str] = Field(min_length=1, max_length=3)
    usage_notes: list[str] = []


class WordForm(BaseModel):
    word: str
    part_of_speech: PartOfSpeech | None = None
    ipa: str | None = None


class WordRelation(BaseModel):
    word: str
    part_of_speech: PartOfSpeech
    differentiator: str | None = None


class Inflections(BaseModel):
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


class GeneratedWord(BaseModel):
    word: str
    pos_tags: list[PartOfSpeech] = Field(min_length=1)
    senses: list[WordSense] = Field(min_length=1)
    synonyms: list[WordRelation] = Field(max_length=4)
    antonyms: list[WordRelation] = Field(max_length=4)
    inflections: Inflections | None = None
    word_family: list[WordForm] = []

    @field_validator('inflections', mode='before')
    @classmethod
    def _empty_inflections_to_none(cls, v: object) -> Inflections | None | object:
        if isinstance(v, dict) and not any(v.values()):
            return None
        return v

    pronunciation: Pronunciation
    etymology: list[Etymology] = []
    common_mistakes: list[str] = Field(max_length=3)
    interesting_fact: str | None = None
    is_wotd: bool = False


class GeneratedMetadata(BaseModel):
    last_generation_date: str
    model: str
    total_generated_words: int
    total_curated_words: int
    words_generated_this_run: int
    remaining_words: int
