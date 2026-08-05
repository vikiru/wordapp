"""Shared ``.env`` loading for wordapp packages.

Every workspace package reads environment variables from a single
``packages/.env`` file. ``load_env()`` is the only dotenv loader in the
repo; call it at the top of an entrypoint before reading config, so that
shell environment variables still take precedence (override is off) but
the shared file fills in the rest.
"""

from __future__ import annotations

from dotenv import load_dotenv

from config import workspace_root

ENV_FILE = workspace_root() / '.env'


def load_env() -> None:
    """Load ``packages/.env`` into the process environment (no override)."""
    load_dotenv(ENV_FILE)
