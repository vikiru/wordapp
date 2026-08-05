"""Central loguru configuration.

This module is the single place where loguru is configured for the workspace
packages. Every other module uses the global loguru logger directly; nothing
else calls ``logger.remove()``/``logger.add()`` so sinks are set up exactly once.
Consumers call :func:`setup_logging` explicitly (e.g. ``setup_logging(name="curate")``).
"""

from __future__ import annotations

import sys

from loguru import logger

from config import workspace_root

LOGS_DIR = workspace_root() / 'logs'


def setup_logging(
    *,
    name: str = 'app',
    console: bool = True,
    rotation: str = '10 MB',
) -> None:
    """Configure loguru sinks. Idempotent: safe to call more than once."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger.remove()
    if console:
        logger.add(sys.stderr, level='INFO')
    logger.add(
        LOGS_DIR / f'{name}_{{time:YYYY-MM-DD}}.log',
        rotation=rotation,
        retention='30 days',
        level='INFO',
        enqueue=True,
    )
