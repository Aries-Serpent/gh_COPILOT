"""Development configuration for the Web GUI.

Mirrors the production structure but with development-friendly defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__all__ = ["DevelopmentConfig"]

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "databases"


@dataclass(frozen=True)
class DevelopmentConfig:
    """Configuration values for development environment."""

    DEBUG: bool = True  # Enable verbose error pages.
    TESTING: bool = True
    DATABASE_PATH: str = str(DATABASE_DIR / "development.db")
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")
    SESSION_COOKIE_SECURE: bool = False  # Allow HTTP during local dev.
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    PREFERRED_URL_SCHEME: str = "http"
    WTF_CSRF_ENABLED: bool = False  # Simplify form testing.
    REMEMBER_COOKIE_SECURE: bool = False
    REMEMBER_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SAMESITE: str = "Lax"
