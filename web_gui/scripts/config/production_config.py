"""Secure production configuration for the Web GUI.

Provides a dataclass with hardened defaults suitable for deployment.
Each field documents its security rationale to aid future maintenance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__all__ = ["ProductionConfig"]

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "databases"


@dataclass(frozen=True)
class ProductionConfig:
    """Configuration values for production environment."""

    DEBUG: bool = False  # Avoid exposing sensitive stack traces.
    TESTING: bool = False
    DATABASE_PATH: str = str(DATABASE_DIR / "production.db")
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "")
    SESSION_COOKIE_SECURE: bool = True  # Send cookies only over HTTPS.
    SESSION_COOKIE_HTTPONLY: bool = True  # Disallow JavaScript access.
    SESSION_COOKIE_SAMESITE: str = "Strict"  # Mitigate CSRF.
    PREFERRED_URL_SCHEME: str = "https"  # Force HTTPS links.
    WTF_CSRF_ENABLED: bool = True  # Enable CSRF protection.
    REMEMBER_COOKIE_SECURE: bool = True  # Persist cookies only via HTTPS.
    REMEMBER_COOKIE_HTTPONLY: bool = True  # Block script access.
    REMEMBER_COOKIE_SAMESITE: str = "Strict"  # Harden persistent cookies.
