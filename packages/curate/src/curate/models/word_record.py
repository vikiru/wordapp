import msgspec

from ..constants import CONCRETE_LEXFILES


class WordRecord(msgspec.Struct, frozen=True, kw_only=True):
    lemma: str
    is_profanity: bool
    has_wn: bool
    is_valid_wn: bool
    is_named_individual: bool
    has_unwanted_hypernym: bool = False
    is_definitional_excluded: bool = False
    pos_set: frozenset[str] = frozenset()
    zipf: float = 0.0
    roots: frozenset[str] = frozenset()
    direct_hypernyms: frozenset[str] = frozenset()
    direct_hyponyms: frozenset[str] = frozenset()
    lexfiles: frozenset[str] = frozenset()
    instance_hypernyms: frozenset[str] = frozenset()
    related_targets: frozenset[str] = frozenset()
    body_parts: frozenset[str] = frozenset()
    definitions: tuple[str, ...] = ()

    def has_non_noun_lexfile(self) -> bool:
        return any(lf.split('.')[0] != 'noun' for lf in self.lexfiles)

    def invalid_wn(self) -> bool:
        return self.has_wn and not self.is_valid_wn

    def concrete_only(self) -> bool:
        return (
            self.roots == frozenset({'physical entity'}) and bool(self.lexfiles) and self.lexfiles <= CONCRETE_LEXFILES
        )

    @classmethod
    def from_cache(cls, cache_bytes: bytes) -> dict[str, 'WordRecord']:
        return msgspec.json.decode(cache_bytes, type=dict[str, WordRecord])
