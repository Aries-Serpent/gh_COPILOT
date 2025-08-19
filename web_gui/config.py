"""Configuration helpers for the Web GUI.

DEBUG is disabled by default to avoid exposing sensitive stack traces.
Set the ``WEB_GUI_DEBUG`` environment variable to ``1`` to enable debug mode
during development.
"""
from __future__ import annotations

import os


def _bool_env(name: str, default: bool) -> bool:
    """Return a boolean read from environment variables."""
    return os.getenv(name, "1" if default else "0").lower() in {"1", "true", "yes"}


# DEBUG defaults to False unless WEB_GUI_DEBUG is explicitly set.
DEBUG: bool = _bool_env("WEB_GUI_DEBUG", False)
