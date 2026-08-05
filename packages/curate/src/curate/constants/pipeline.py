# Pipeline thresholds and derived-run constants. Provenance: magic numbers and
# the targeted-leak list extracted verbatim from main.py (pre-refactor) so the
# pipeline references named constants instead of literals.

from config import workspace_root

# Word-length eligibility window (from Step 1 in the old main.py)
MIN_WORD_LENGTH = 4
MAX_WORD_LENGTH = 14

# Zipf-frequency window for the curated list. A word must land in this window
# for BOTH its raw form and its resolved lemma to be kept.
ZIPF_MIN_THRESHOLD = 2.75
ZIPF_MAX_THRESHOLD = 3.20

# Minimum stem length for the -ed redundant-derivation rule (avoids collapsing
# short words like 'bed' -> 'b').
ED_STEM_MIN_LENGTH = 5

# Pre-computed WordNet metadata cache built by build_cache.py
CACHE_FILE = workspace_root() / 'curate' / 'web2_wordnet_cache.json'

# Targeted leak words: substring check over the raw word and its base lemma,
# catching clinical/STEM/junk terms that slip past the structural gates.
TARGETED_LEAKS = (
    'carcinogen',
    'carpal',
    'aorta',
    'cortex',
    'cyst',
    'diphtheria',
    'eczema',
    'emphysema',
    'femur',
    'lactate',
    'lymph',
    'vertebra',
    'weld',
    'whistle',
    'xenophobia',
    'phobia',
    'zeta',
    'zoology',
    'zigzag',
    'zonal',
    'whence',
    'wherefore',
    'whiny',
    'whisper',
    'whitehead',
    'whiten',
    'whitish',
    'yellowish',
    'reddish',
    'bluish',
    'greenish',
    'purplish',
    'pinkish',
    'blackish',
    'adipose',
    'alveolar',
    'anabolic',
    'anaerobic',
    'antibacterial',
    'atrial',
    'carotid',
    'celiac',
    'cochlear',
    'cornea',
    'cytoplasm',
    'dermal',
    'dermatology',
    'dielectric',
    'electrostatic',
    'ischemic',
    'necrosis',
    'ventricle',
)
