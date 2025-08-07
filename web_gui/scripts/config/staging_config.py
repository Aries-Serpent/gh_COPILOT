"""Staging configuration for the Web GUI.

Mirrors the production structure but with staging defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__all__ = ["StagingConfig"]

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "databases"


@dataclass(frozen=True)
class StagingConfig:
    """Configuration values for staging environment."""

    DEBUG: bool = False
    TESTING: bool = False
    DATABASE_PATH: str = str(DATABASE_DIR / "staging.db")
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "staging_secret_key")
    SESSION_COOKIE_SECURE: bool = False  # Staging may run over HTTP.
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    PREFERRED_URL_SCHEME: str = "https"
    WTF_CSRF_ENABLED: bool = True
    REMEMBER_COOKIE_SECURE: bool = False
    REMEMBER_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SAMESITE: str = "Lax"
