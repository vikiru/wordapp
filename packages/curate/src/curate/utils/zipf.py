from ..constants import ZIPF_MAX_THRESHOLD, ZIPF_MIN_THRESHOLD


def within_zipf_window(zipf_raw: float, zipf_lemma: float) -> bool:
    return (
        ZIPF_MIN_THRESHOLD <= zipf_raw <= ZIPF_MAX_THRESHOLD and ZIPF_MIN_THRESHOLD <= zipf_lemma <= ZIPF_MAX_THRESHOLD
    )
