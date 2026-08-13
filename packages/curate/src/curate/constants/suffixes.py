# Morphological suffix blocklists

# Clinical/STEM suffixes. Any word whose lemma ends in one of these is
# medical jargon, not flair vocabulary.
CLINICAL_SUFFIXES = (
    'itis',
    'oma',
    'osis',
    'emia',
    'ectomy',
    'otomy',
    'emic',
    'ase',
    'zoic',
    'phage',
    'mycin',
    'surgery',
    'therapy',
)

# Bureaucratic bloat suffixes. Business/procedural word-forms with no flair.
BUREAUCRATIC_SUFFIXES = (
    'ization',
    'bility',
    'fulness',
    'lessly',
    'istically',
    'ously',
    'ively',
    'ably',
)

# Safe Excluded Suffixes (clinical + bureaucratic + mechanical word-forms).
# Combined into one tuple so a single endswith() scan covers all of them.
EXCLUDED_SUFFIXES = (
    CLINICAL_SUFFIXES
    + BUREAUCRATIC_SUFFIXES
    + (
        'ings',
        'ing',
        'ness',
        'ability',
        'alness',
        'ally',
        'ically',
        'istic',
        'istical',
        'ize',
        'lize',
        'ded',
        'led',
        'ted',
        'ned',
        'ated',
        'ation',
        'phobia',
        'phobic',
        'ical',
        'ly',
        'ist',
        'ism',
        'ship',
        'hood',
        'ward',
        'wards',
        'wise',
        'ify',
        'ze',
        'ive',
    )
)
