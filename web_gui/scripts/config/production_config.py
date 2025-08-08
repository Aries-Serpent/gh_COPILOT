"""Secure production configuration for the Web GUI.

Provides a dataclass with hardened defaults suitable for deployment.
Each field documents its security rationale to aid future maintenance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["ProductionConfig"]

BASE_DIR = Path(__file__).resolve().parents[3]
DATABASE_DIR = BASE_DIR / "databases"


def _bool_env(name: str, default: bool) -> bool:
    """Return a boolean from environment variables."""
    return os.getenv(name, "1" if default else "0").lower() in {"1", "true", "yes"}


def _int_env(name: str, default: int) -> int:
    """Return an integer from environment variables with validation."""
    try:
        return int(os.getenv(name, str(default)))
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid integer for {name}") from exc


@dataclass(frozen=True)
class ProductionConfig:
    """Configuration values for production environment."""

    DEBUG: bool = field(
        default_factory=lambda: _bool_env("WEB_GUI_DEBUG", False)
    )  # Avoid exposing sensitive stack traces.
    TESTING: bool = field(default_factory=lambda: _bool_env("WEB_GUI_TESTING", False))
    DATABASE_PATH: str = field(
        default_factory=lambda: os.getenv("WEB_GUI_DATABASE_PATH", str(DATABASE_DIR / "production.db"))
    )
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("FLASK_SECRET_KEY", ""))
    SESSION_COOKIE_SECURE: bool = field(
        default_factory=lambda: _bool_env("WEB_GUI_SESSION_COOKIE_SECURE", True)
    )  # Send cookies only over HTTPS.
    SESSION_COOKIE_HTTPONLY: bool = field(
        default_factory=lambda: _bool_env("WEB_GUI_SESSION_COOKIE_HTTPONLY", True)
    )  # Disallow JavaScript access.
    SESSION_COOKIE_SAMESITE: str = field(
        default_factory=lambda: os.getenv("WEB_GUI_SESSION_COOKIE_SAMESITE", "Strict")
    )  # Mitigate CSRF.
    PREFERRED_URL_SCHEME: str = field(
        default_factory=lambda: os.getenv("WEB_GUI_PREFERRED_URL_SCHEME", "https")
    )  # Force HTTPS links.
    WTF_CSRF_ENABLED: bool = field(
        default_factory=lambda: _bool_env("WEB_GUI_WTF_CSRF_ENABLED", True)
    )  # Enable CSRF protection.
    REMEMBER_COOKIE_SECURE: bool = field(
        default_factory=lambda: _bool_env("WEB_GUI_REMEMBER_COOKIE_SECURE", True)
    )  # Persist cookies only via HTTPS.
    REMEMBER_COOKIE_HTTPONLY: bool = field(
        default_factory=lambda: _bool_env("WEB_GUI_REMEMBER_COOKIE_HTTPONLY", True)
    )  # Block script access.
    REMEMBER_COOKIE_SAMESITE: str = field(
        default_factory=lambda: os.getenv("WEB_GUI_REMEMBER_COOKIE_SAMESITE", "Strict")
    )  # Harden persistent cookies.
    MAX_CONTENT_LENGTH: int = field(
        default_factory=lambda: _int_env("WEB_GUI_MAX_CONTENT_LENGTH", 1_048_576)
    )

    def __post_init__(self) -> None:
        if not self.SECRET_KEY:
            raise ValueError("FLASK_SECRET_KEY must be set in production.")
        db_path = Path(self.DATABASE_PATH)
        if not db_path.is_file():
            raise ValueError(f"Database not found at {db_path}")
        if not self.SESSION_COOKIE_SECURE:
            raise ValueError("SESSION_COOKIE_SECURE must be enabled in production.")
        if not self.WTF_CSRF_ENABLED:
            raise ValueError("WTF_CSRF_ENABLED must be True in production.")
        if self.PREFERRED_URL_SCHEME != "https":
            raise ValueError("PREFERRED_URL_SCHEME must be 'https' in production.")
        if self.MAX_CONTENT_LENGTH <= 0:
            raise ValueError("MAX_CONTENT_LENGTH must be positive.")
