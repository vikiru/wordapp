"""Data package models."""

from data.models.archive import ArchiveEntry, ArchiveFile, WordsFile, WordsTodayFile, WotdFile
from data.models.word import (
    EtymologyDoc,
    InflectionsDoc,
    PronunciationDoc,
    WordDocument,
    WordFormDoc,
    WordRelationDoc,
    WordSenseDoc,
)

__all__ = [
    'WordsFile',
    'WordsTodayFile',
    'WotdFile',
    'ArchiveEntry',
    'ArchiveFile',
    'EtymologyDoc',
    'InflectionsDoc',
    'PronunciationDoc',
    'WordDocument',
    'WordFormDoc',
    'WordRelationDoc',
    'WordSenseDoc',
]
