"""Word-list constants for the curation pipeline.

Every curated list carries a why-comment above it explaining its purpose and
its provenance/change policy. Adding or removing a word is a one-line edit to
the owning constant — lists are referenced from here, never duplicated.
"""

# Whitelist building blocks

# Dedicated Domain List: Grammatical & Linguistic Technical Terms.
# These survive every gate because they are the vocabulary of the domain the
# pipeline is about, not generic prose. Add a term only if it is a standard
# grammar/linguistics technical term.
GRAMMAR_LINGUISTIC_TERMS = {
    'synonym',
    'antonym',
    'hypernym',
    'hyponym',
    'meronym',
    'holonym',
    'homonym',
    'homophone',
    'homograph',
    'monosemy',
    'lemma',
    'lemmatization',
    'stemming',
    'morpheme',
    'morphology',
    'syntax',
    'semantics',
    'pragmatics',
    'phoneme',
    'phonology',
    'phonetics',
    'etymology',
    'lexicon',
    'lexicography',
    'grammar',
    'parsing',
    'noun',
    'verb',
    'adjective',
    'adverb',
    'pronoun',
    'preposition',
    'conjunction',
    'interjection',
    'participle',
    'infinitive',
    'gerund',
    'predicate',
    'clause',
    'tenses',
    'declension',
    'conjugation',
    'collocation',
    'idiom',
    'metaphor',
    'simile',
    'synecdoche',
    'metonymy',
    'hyperbole',
    'oxymoron',
    'anaphora',
    'epistrophe',
    'alliteration',
    'assonance',
    'consonance',
    'onomatopoeia',
    'euphony',
    'cacophony',
}

# High-Flair Behavioral Archetypes (Rescued from 'person' hypernym tree).
# Personality/character words that the person-subtree root exclusion would
# otherwise drop. Add an archetype only if it names a human behavioral type.
BEHAVIORAL_ARCHETYPES = {
    'sycophant',
    'maverick',
    'martinet',
    'polymath',
    'miscreant',
    'dilettante',
    'pariah',
    'charlatan',
    'luminary',
    'stoic',
    'virtuoso',
    'archetype',
    'visionary',
    'vanguard',
}

# High-Flair Base Words Ending in Common Suffix Letters (-ish, -ion, -ment, -ery, -red).
# Rescued because the structural suffix-stem rules would strip them; they are
# base words, not derivations. Add only base words that are not derived forms.
HIGH_FLAIR_BASE_WORDS = {
    # -ish verbs/nouns
    'flourish',
    'vanquish',
    'embellish',
    'relish',
    'blemish',
    'impoverish',
    'skirmish',
    'brandish',
    'garnish',
    # -ion elite nouns
    'oblivion',
    'bastion',
    'legion',
    'coercion',
    'clarion',
    # -ment high-flair bases
    'torment',
    'detriment',
    # -ery concepts
    'treachery',
    'mockery',
    'mastery',
    'reverie',
    # -red & structures
    'kindred',
}

# Primary Core Whitelist: High Quality English Vocabulary (Expressive Nouns, Verbs & Adjectives).
# The foundation of the output vocabulary. Add a word only after a manual
# flair judgment; removals are recorded in EXCLUDED_WORDS, not edited here.
PRIMARY_CORE_WHITELIST = (
    {
        'ire',
        'wrath',
        'serendipity',
        'superfluous',
        'ineffable',
        'ephemeral',
        'mellifluous',
        'petrichor',
        'synergy',
        'eloquence',
        'resplendent',
        'quintessence',
        'vivacious',
        'gossamer',
        'silhouette',
        'camaraderie',
        'ethereal',
        'incandescent',
        'luminous',
        'luminary',
        'surreptitious',
        'paradigm',
        'reverie',
        'opulent',
        'nebulous',
        'serendipitous',
        'solitude',
        'epitome',
        'stoic',
        'enigma',
        'paradox',
        'elegy',
        'eulogy',
        'zenith',
        'dichotomy',
        'enthrall',
        'exquisite',
        'fastidious',
        'gratify',
        'haughty',
        'impeccable',
        'juxtapose',
        'kindred',
        'lucid',
        'magnanimous',
        'ostentatious',
        'pragmatic',
        'quaint',
        'resilient',
        'scrutinize',
        'tenacious',
        'ubiquitous',
        'vex',
        'whimsical',
        'yearn',
        'zealous',
        'aesthetic',
        'enchant',
        'allure',
        'sublime',
        'grandeur',
        'profound',
        'solace',
        'vanity',
        'veracity',
        'vibrant',
        'vigilant',
        'vindicate',
        'virtuoso',
        'wistful',
        'abhor',
        'abjure',
        'abrogate',
        'abscond',
        'abstemious',
        'acumen',
        'admonish',
        'adroit',
        'adulation',
        'affable',
        'affinity',
        'aggrandize',
        'alacrity',
        'alliteration',
        'altruism',
        'amalgamate',
        'ambiguity',
        'ameliorate',
        'anachronism',
        'anathema',
        'anecdote',
        'anguish',
        'antecedent',
        'antipathy',
        'antiquated',
        'antithesis',
        'apathy',
        'aphorism',
        'apocryphal',
        'appease',
        'arbitrary',
        'arcane',
        'archaic',
        'archetype',
        'ardent',
        'arduous',
        'articulate',
        'ascribe',
        'aspire',
        'assail',
        'assiduous',
        'assuage',
        'astute',
        'audacity',
        'auspicious',
        'austere',
        'authentic',
        'avarice',
        'avid',
        'castigate',
        'reprieve',
        'guile',
        'respite',
        'foreboding',
        'stagnant',
        'amplify',
        'radiance',
        'deluge',
        'rejuvenate',
        'acquiesce',
        'resonance',
        'fracas',
        'eschew',
        'saunter',
        'sublimate',
        'obliteration',
        'insight',
        'dissemble',
        'charlatan',
        'equanimity',
        'tempest',
        'explicate',
        'serenity',
        'repose',
        'introspect',
        'bode',
        'transpire',
        'rekindle',
        'syncretise',
        'recant',
        'forswear',
        'languor',
        'shimmer',
        'extirpate',
        'effusion',
        'eminence',
        'rebuttal',
        'melancholy',
        'berserk',
        'fathom',
    }
    | BEHAVIORAL_ARCHETYPES
    | HIGH_FLAIR_BASE_WORDS
)

# Rescued from the invalid-46 set: good flair words that only fail due to
# over-broad definition/root exclusion flags. Whitelisted so they survive.
RESCUE_WORDS = {
    'allegory',
    'amity',
    'babble',
    'cavern',
    'cleft',
    'dynamism',
    'fizz',
    'flutter',
    'heave',
    'hiss',
    'scour',
}

# Words kept despite matching the structural un- prefix rule (UN_PREFIX_KEEP).
# Good negated/participial words the stem rule would otherwise drop.
UN_PREFIX_KEEP = {
    'unfathomable',
    'unscathed',
    'untamed',
    'unspoken',
    'unsung',
    'unorthodox',
    'unfettered',
    'unravel',
    'unison',
}

# Words kept despite matching the structural -ed suffix rule (ED_SUFFIX_KEEP).
# Strong participial adjectives that would otherwise be stripped as
# derivations of their verb stems.
ED_SUFFIX_KEEP = {
    'tempered',
    'shrouded',
    'abridged',
    'antiquated',
    'bewildered',
    'cloaked',
    'depraved',
    'deranged',
    'dismayed',
    'enamored',
    'engrossed',
    'perplexed',
}

# -ist / -ism / -ology / -ion suffix words worth keeping despite the
# structural suffix rule (NOUN_SUFFIX_KEEP). All other suffix-stem words drop.
NOUN_SUFFIX_KEEP = {
    'volition',
}

# Expressive keep-band words that pass every structural gate but were still
# absent from the output (found via the full drop-reason audit of the 3,583
# expressive keep-band web2 words). Manually vetted, -ism words excluded.
EXPRESSIVE_RESCUE = {
    'amiable',
    'atrocious',
    'buoyant',
    'capricious',
    'cleave',
    'complacency',
    'coy',
    'deference',
    'delirious',
    'desist',
    'divergence',
    'exuberance',
    'forsaken',
    'hyperbolic',
    'indecision',
    'leniency',
    'melodramatic',
    'monogamous',
    'pompous',
    'pretentious',
    'proverbial',
    'repressive',
    'repulsive',
    'retaliatory',
    'fortitude',
    'finesse',
    'foresight',
    'nefarious',
    'placid',
    'rapture',
    'renown',
    'shrewd',
    'succinct',
    'tacit',
    'tenuous',
    'verve',
    'forlorn',
    'malevolent',
    'ornate',
    'penchant',
    'salient',
    'spurious',
    'conjure',
    'elicit',
    'exorbitant',
    'flagrant',
    'distraught',
    'demeanor',
    'indignant',
    'meager',
    'cursory',
    'fraught',
    'tantamount',
    'staunch',
    'exuberant',
    'brisk',
    'vigor',
    'savor',
    'dapper',
    'exacerbate',
}

# Unified Whitelist Combined (Primary Core + Grammatical Extras + Rescues +
# un-/ed-stem-rule guards + expressive rescue). This is the master whitelist:
# a whitelisted word bypasses ALL rejection gates.
WHITELIST = (
    PRIMARY_CORE_WHITELIST
    | GRAMMAR_LINGUISTIC_TERMS
    | RESCUE_WORDS
    | UN_PREFIX_KEEP
    | ED_SUFFIX_KEEP
    | EXPRESSIVE_RESCUE
)

# Map British spellings to their American canonical forms so only the
# canonical form survives the dedup step.
SPELLING_VARIANTS = {
    'meagre': 'meager',
    'savour': 'savor',
    'tranquillity': 'tranquility',
}

# Manual blocklist for named individuals the instance-hypernym rule cannot
# catch: farrow/mirza/pilar have no instance_hypernyms at all, and snoopy's
# adjective lexfile defeats the non-noun guard. faust/alamo are now handled
# by NAMED_INSTANCE_CATEGORIES and removed from here.
NAMED_INDIVIDUAL_BLOCKLIST = {'farrow', 'mirza', 'pilar', 'snoopy'}
