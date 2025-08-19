"""Configuration helpers for the Web GUI.

DEBUG defaults to ``False`` to avoid exposing sensitive stack traces.
Set the ``WEB_GUI_DEBUG`` environment variable to ``1`` when developing
to temporarily enable debug mode. Avoid enabling this in production.
"""
from __future__ import annotations

import os


def _bool_env(name: str, default: bool) -> bool:
    """Return a boolean read from environment variables."""
    return os.getenv(name, "1" if default else "0").lower() in {"1", "true", "yes"}


# DEBUG defaults to False; set WEB_GUI_DEBUG=1 only for development.
DEBUG: bool = _bool_env("WEB_GUI_DEBUG", False)
