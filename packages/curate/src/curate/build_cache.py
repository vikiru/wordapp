import os
import re
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import msgspec
import wn
from english_words import get_english_words_set
from glin_profanity import Filter
from loguru import logger
from simplemma import Lemmatizer
from simplemma.strategies import DefaultStrategy
from simplemma.strategies.dictionaries import DefaultDictionaryFactory
from wordfreq import zipf_frequency

from config import workspace_root
from config.logger import setup_logging
from curate.constants import (
    CACHE_FILE,
    DEFINITION_EXCLUSION_KEYWORDS,
    NAMED_INDIVIDUAL_DEFINITION_REGEX,
    TAXONOMY_ROOT_EXCLUSIONS,
)
from curate.utils import WordRecord

setup_logging(name='curate')

CACHE_PATH = CACHE_FILE
CHUNK_SIZE = 5000
MAX_WORKERS = int(os.environ.get('CACHE_BUILD_WORKERS', os.cpu_count() or 2))

# instance_hypernym: authoritative signal for named entities (people, deities, places).
REL_INSTANCE_HYPERNYM = 'instance_hypernym'

# derivation/pertainym targets' lexfiles discriminate clinical adj.pert words.
REL_DERIVATION = 'derivation'
REL_PERTAINYM = 'pertainym'

# glin-profanity's English dictionary misses these (exact-match additions).
# Loaded from the gitignored profanity.txt so edits don't touch the codebase.
PROFANITY_CUSTOM_WORDS = [
    w.strip() for w in (workspace_root() / 'curate' / 'profanity.txt').read_text().splitlines() if w.strip()
]

# Per-worker state, set by _init_worker
_ewn: wn.Wordnet | None = None
_lemmatizer: Lemmatizer | None = None
_profanity_filter: Filter | None = None
_unwanted_synset_ids: frozenset[str] = frozenset()
_entity_ids: frozenset[str] = frozenset()
_pure_body_nouns: frozenset[str] = frozenset()

# Synsets are heavily shared across words, so memoize per synset.id.
_memo_roots: dict[str, frozenset[str]] = {}
_memo_unwanted: dict[str, bool] = {}
_memo_direct_hypernyms: dict[str, frozenset[str]] = {}
_memo_direct_hyponyms: dict[str, frozenset[str]] = {}
_memo_definitional: dict[str, bool] = {}
_memo_named: dict[str, bool] = {}
_memo_inst_hyper: dict[str, frozenset[str]] = {}
_memo_related_targets: dict[str, frozenset[str]] = {}


def _load_wordnet() -> wn.Wordnet:
    """Load the OEWN 2025+ wordnet, hinting at the install command if the data is missing."""
    try:
        return wn.Wordnet('oewn:2025+')
    except wn.Error:
        logger.error(
            'curate: Failed to load WordNet data (oewn:2025+); '
            'run `python -m wn download oewn:2025+` to install it.'
        )
        raise


def _init_worker(
    unwanted_synset_ids_: set[str] | frozenset[str],
    entity_ids_: set[str] | frozenset[str],
    pure_body_nouns_: set[str] | frozenset[str],
) -> None:
    global _ewn, _lemmatizer, _profanity_filter
    global _unwanted_synset_ids, _entity_ids, _pure_body_nouns
    _unwanted_synset_ids = frozenset(unwanted_synset_ids_)
    _entity_ids = frozenset(entity_ids_)
    _pure_body_nouns = frozenset(pure_body_nouns_)
    _ewn = _load_wordnet()
    _profanity_filter = Filter(
        {
            'languages': ['english'],
            'word_boundaries': True,
            'detect_leetspeak': False,
            'cache_results': True,
            'max_cache_size': 50000,
            'custom_words': PROFANITY_CUSTOM_WORDS,
        }
    )
    _lemmatizer = Lemmatizer(
        lemmatization_strategy=DefaultStrategy(
            dictionary_factory=DefaultDictionaryFactory(cache_max_size=16),
        )
    )
    _memo_roots.clear()
    _memo_unwanted.clear()
    _memo_direct_hypernyms.clear()
    _memo_direct_hyponyms.clear()
    _memo_definitional.clear()
    _memo_named.clear()
    _memo_inst_hyper.clear()
    _memo_related_targets.clear()


def _build_pure_body_nouns(ewn: wn.Wordnet) -> set[str]:
    pure_body = set()
    for w in ewn.words():
        synsets = w.synsets()
        if not synsets:
            continue
        if all(s.lexfile() == 'noun.body' for s in synsets):
            pure_body.add(w.lemma().lower())
    return pure_body


def _first_lemma(synset: wn.Synset) -> str | None:
    lemmas = synset.lemmas()
    return lemmas[0].lower() if lemmas else None


def _is_root(synset: wn.Synset) -> bool:
    if synset.id in _entity_ids:
        return False
    hypernyms = synset.hypernyms()
    if not hypernyms:
        return True
    return all(h.id in _entity_ids for h in hypernyms)


def _roots(synset: wn.Synset) -> frozenset[str]:
    sid = synset.id
    cached = _memo_roots.get(sid)
    if cached is not None:
        return cached
    acc = set()
    for parent in synset.hypernyms():
        lemma = _first_lemma(parent)
        if lemma and _is_root(parent):
            acc.add(lemma)
        acc |= _roots(parent)
    frozen = frozenset(acc)
    _memo_roots[sid] = frozen
    return frozen


def _has_unwanted_ancestor(synset: wn.Synset) -> bool:
    sid = synset.id
    if sid in _memo_unwanted:
        return _memo_unwanted[sid]
    if sid in _unwanted_synset_ids:
        _memo_unwanted[sid] = True
        return True
    for parent in synset.hypernyms():
        if _has_unwanted_ancestor(parent):
            _memo_unwanted[sid] = True
            return True
    _memo_unwanted[sid] = False
    return False


def _direct_hypernym_lemmas(synset: wn.Synset) -> frozenset[str]:
    sid = synset.id
    if sid not in _memo_direct_hypernyms:
        acc = frozenset(lemma for parent in synset.hypernyms() if (lemma := _first_lemma(parent)))
        _memo_direct_hypernyms[sid] = acc
    return _memo_direct_hypernyms[sid]


def _direct_hyponym_lemmas(synset: wn.Synset) -> frozenset[str]:
    sid = synset.id
    if sid not in _memo_direct_hyponyms:
        acc = frozenset(lemma for child in synset.hyponyms() if (lemma := _first_lemma(child)))
        _memo_direct_hyponyms[sid] = acc
    return _memo_direct_hyponyms[sid]


def _instance_hypernym_lemmas(synset: wn.Synset) -> frozenset[str]:
    sid = synset.id
    if sid not in _memo_inst_hyper:
        acc = frozenset(lemma for t in synset.get_related(REL_INSTANCE_HYPERNYM) if (lemma := _first_lemma(t)))
        _memo_inst_hyper[sid] = acc
    return _memo_inst_hyper[sid]


def _related_target_lemmas(synset: wn.Synset) -> frozenset[str]:
    sid = synset.id
    if sid not in _memo_related_targets:
        acc = set()
        for sense in synset.senses():
            for rel in sense.get_related(REL_DERIVATION):
                lemma = rel.word().lemma().lower()
                if lemma and lemma.isalpha():
                    acc.add(lemma)
            for rel in sense.get_related(REL_PERTAINYM):
                lemma = rel.word().lemma().lower()
                if lemma and lemma.isalpha():
                    acc.add(lemma)
        _memo_related_targets[sid] = frozenset(acc)
    return _memo_related_targets[sid]


def _exclusion_flags(synset: wn.Synset) -> tuple[bool, bool]:
    sid = synset.id
    if sid not in _memo_definitional:
        defn = (synset.definition() or '').lower()
        _memo_definitional[sid] = synset.pos == 'n' and any(k in defn for k in DEFINITION_EXCLUSION_KEYWORDS)
        _memo_named[sid] = re.search(NAMED_INDIVIDUAL_DEFINITION_REGEX, defn) is not None
    return _memo_definitional[sid], _memo_named[sid]


def _resolve_base_lemma(word: str) -> str:
    ewn = _ewn
    lemmatizer = _lemmatizer
    assert ewn is not None and lemmatizer is not None
    words = ewn.words(word)
    if words:
        w_obj = words[0]
        derived = w_obj.derived_words()
        if derived:
            shortest: list[str] = sorted(
                [d.lemma().lower() for d in derived if d.lemma().isalpha()],
                key=len,
            )
            if shortest and len(shortest[0]) < len(word):
                return shortest[0]
        return w_obj.lemma().lower()
    try:
        return lemmatizer.lemmatize(word, 'en').lower()
    except Exception:  # noqa: BLE001
        return word.lower()


def _no_synset_record(word: str, is_profane: bool) -> WordRecord:
    return WordRecord(
        lemma=word,
        is_profanity=is_profane,
        has_wn=False,
        is_valid_wn=False,
        is_named_individual=False,
    )


def _process_chunk(
    words: list[str],
) -> tuple[dict[str, WordRecord], tuple[float, float, float, float, int]]:
    assert _ewn is not None and _profanity_filter is not None
    t_zipf = t_lemma = t_prof = t_syn = 0.0
    n_wn = 0
    out: dict[str, WordRecord] = {}
    for w in words:
        # Profanity for every word: main.py re-checks it on base lemmas later.
        t0 = time.perf_counter()
        is_profane = _profanity_filter.check_profanity(w).get('contains_profanity', False)
        t_prof += time.perf_counter() - t0

        t0 = time.perf_counter()
        synsets = _ewn.synsets(w)
        t_syn += time.perf_counter() - t0
        if not synsets:
            out[w] = _no_synset_record(w, is_profane)
            continue

        t0 = time.perf_counter()
        lemma_val = _resolve_base_lemma(w)
        t_lemma += time.perf_counter() - t0

        t0 = time.perf_counter()
        zipf_val = round(zipf_frequency(w, 'en'), 3)
        t_zipf += time.perf_counter() - t0

        t0 = time.perf_counter()
        n_wn += 1
        has_unwanted = False
        is_definitional_excluded = False
        is_named_individual = False
        valid_pos: list[str] = []
        roots = set()
        direct_hypernyms = set()
        direct_hyponyms = set()
        lexfiles = set()
        instance_hypernyms = set()
        related_targets = set()
        definitions: list[str] = []

        for s in synsets:
            valid_pos.append(s.pos)
            if _has_unwanted_ancestor(s):
                has_unwanted = True
            direct_hypernyms |= _direct_hypernym_lemmas(s)
            direct_hyponyms |= _direct_hyponym_lemmas(s)
            roots |= _roots(s)
            lexfile = s.lexfile()
            if lexfile:
                lexfiles.add(lexfile)
            instance_hypernyms |= _instance_hypernym_lemmas(s)
            related_targets |= _related_target_lemmas(s)
            defn_excluded, named = _exclusion_flags(s)
            if defn_excluded:
                is_definitional_excluded = True
            if named:
                is_named_individual = True
            if len(definitions) < 3:
                defn = (s.definition() or '').lower()
                if defn:
                    definitions.append(defn[:120])
        t_syn += time.perf_counter() - t0

        out[w] = WordRecord(
            lemma=lemma_val,
            is_profanity=is_profane,
            has_wn=True,
            is_valid_wn=not has_unwanted and not is_definitional_excluded,
            is_named_individual=is_named_individual,
            has_unwanted_hypernym=has_unwanted,
            is_definitional_excluded=is_definitional_excluded,
            pos_set=frozenset(valid_pos),
            zipf=zipf_val,
            roots=frozenset(roots),
            direct_hypernyms=frozenset(direct_hypernyms),
            direct_hyponyms=frozenset(direct_hyponyms),
            lexfiles=frozenset(lexfiles),
            instance_hypernyms=frozenset(instance_hypernyms),
            related_targets=frozenset(related_targets),
            body_parts=frozenset(related_targets & _pure_body_nouns),
            definitions=tuple(definitions),
        )
    return out, (t_zipf, t_lemma, t_prof, t_syn, n_wn)


def _build_unwanted_ids(ewn: wn.Wordnet) -> set[str]:
    unwanted = set()
    for target in TAXONOMY_ROOT_EXCLUSIONS:
        for s in ewn.synsets(target):
            unwanted.add(s.id)
            stack = list(s.hyponyms())
            visited = set()
            while stack:
                curr = stack.pop()
                if curr.id in visited:
                    continue
                visited.add(curr.id)
                unwanted.add(curr.id)
                stack.extend(curr.hyponyms())
    return unwanted


def _print_progress(done: int, total_words: int, loop_start: float) -> None:
    elapsed = time.perf_counter() - loop_start
    rate = done / elapsed if elapsed > 0 else 0
    eta = (total_words - done) / rate if rate > 0 else 0
    logger.debug(
        'curate: Processed {:,} / {:,} words in {:.1f}s ({:.0f} words/s, ETA {:.1f} min).',
        done,
        total_words,
        elapsed,
        rate,
        eta / 60,
    )


def build_full_cached_metadata() -> None:
    start_time = time.perf_counter()
    ewn = _load_wordnet()

    t0 = time.perf_counter()
    unwanted_synset_ids = _build_unwanted_ids(ewn)
    t_unwanted = time.perf_counter() - t0

    t0 = time.perf_counter()
    entity_ids = {s.id for s in ewn.synsets('entity')}
    t_entity = time.perf_counter() - t0

    t0 = time.perf_counter()
    pure_body_nouns = _build_pure_body_nouns(ewn)
    t_pure_body = time.perf_counter() - t0

    t0 = time.perf_counter()
    raw_words = sorted({w.lower() for w in get_english_words_set(['web2'], lower=False)})
    total_words = len(raw_words)
    t_words = time.perf_counter() - t0
    logger.debug(
        'curate: Pre-analysis: {:,} unwanted synsets in {:.2f}s | {:,} entity synsets in {:.2f}s | {:,} pure-body nouns in {:.2f}s | {:,} words loaded in {:.2f}s.',
        len(unwanted_synset_ids),
        t_unwanted,
        len(entity_ids),
        t_entity,
        len(pure_body_nouns),
        t_pure_body,
        total_words,
        t_words,
    )

    chunks = [raw_words[i : i + CHUNK_SIZE] for i in range(0, total_words, CHUNK_SIZE)]

    cache_data: dict[str, WordRecord] = {}
    t_zipf = t_lemma = t_prof = t_syn = 0.0
    n_wn = 0
    done = 0
    loop_start = time.perf_counter()

    if MAX_WORKERS <= 1:
        _init_worker(unwanted_synset_ids, entity_ids, pure_body_nouns)
        for chunk in chunks:
            partial, stats = _process_chunk(chunk)
            cache_data.update(partial)
            t_zipf += stats[0]
            t_lemma += stats[1]
            t_prof += stats[2]
            t_syn += stats[3]
            n_wn += stats[4]
            done += len(partial)
            _print_progress(done, total_words, loop_start)
    else:
        with ProcessPoolExecutor(
            max_workers=MAX_WORKERS,
            initializer=_init_worker,
            initargs=(unwanted_synset_ids, entity_ids, pure_body_nouns),
        ) as executor:
            futures = [executor.submit(_process_chunk, chunk) for chunk in chunks]
            for future in as_completed(futures):
                partial, stats = future.result()
                cache_data.update(partial)
                t_zipf += stats[0]
                t_lemma += stats[1]
                t_prof += stats[2]
                t_syn += stats[3]
                n_wn += stats[4]
                done += len(partial)
                _print_progress(done, total_words, loop_start)

    loop_elapsed = time.perf_counter() - loop_start

    t0 = time.perf_counter()
    CACHE_PATH.write_bytes(msgspec.json.encode(cache_data))
    t_dump = time.perf_counter() - t0

    elapsed = time.perf_counter() - start_time
    logger.info('curate: Built metadata cache for {:,} words in {:.2f}s.', len(cache_data), elapsed)
    logger.debug('curate: Loop: {:.1f}s ({:.0f} words/s overall).', loop_elapsed, total_words / loop_elapsed)
    unit = 'CPU' if MAX_WORKERS > 1 else 'wall'
    logger.debug(
        'curate: Timing ({}): zipf {:.1f}s | lemma {:.1f}s | profanity {:.1f}s | wordnet {:.1f}s ({:.1f} ms/wn-word, {:,} wn words) | msgspec dump {:.1f}s.',
        unit,
        t_zipf,
        t_lemma,
        t_prof,
        t_syn,
        t_syn / max(n_wn, 1) * 1000,
        n_wn,
        t_dump,
    )


if __name__ == '__main__':
    build_full_cached_metadata()
