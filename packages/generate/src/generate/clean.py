"""Delete all generated artifacts from the generate directory."""

from __future__ import annotations

from loguru import logger

from config.logger import setup_logging
from generate.utils.io import GENERATED_DATA_FILE, GENERATED_WORDS_FILE, GENERATION_METADATA_FILE


def main() -> int:
    setup_logging(name='generate-clean')
    targets = (GENERATED_WORDS_FILE, GENERATED_DATA_FILE, GENERATION_METADATA_FILE)
    removed = [path for path in targets if path.exists()]
    for path in removed:
        path.unlink()
    if removed:
        logger.info('generate: Deleted {}.', ', '.join(sorted(path.name for path in removed)))
    else:
        logger.info('generate: No generated files to clean.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
