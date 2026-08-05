"""Filesystem anchors shared by wordapp packages.

The single non-brittle way to locate the ``packages/`` workspace root. Every
module that needs to reach ``packages/logs``, ``packages/.env``, or another
sibling package walks up with :func:`workspace_root()` instead of hardcoding
``Path(__file__).resolve().parents[N]`` (which breaks the moment a file moves
depth).
"""

from __future__ import annotations

from pathlib import Path


def workspace_root() -> Path:
    """Walk up from this module to the workspace root (the dir with ``[tool.uv.workspace]``).

    Returns the packages/ directory, robust to this module being relocated
    within the tree.
    """
    current = Path(__file__).resolve().parent
    for parent in (current, *current.parents):
        marker = parent / 'pyproject.toml'
        if marker.exists() and 'tool.uv.workspace' in marker.read_text(encoding='utf-8'):
            return parent
    raise RuntimeError('Could not locate packages/ workspace root')
