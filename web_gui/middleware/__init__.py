"""Convenience helpers for applying middleware to a Flask app."""

from flask import Flask

from .input_validation import input_validation_middleware
from .rate_limiting import rate_limiting_middleware
from .security_headers import security_headers_middleware
from .session_management import session_management_middleware


def init_app(app: Flask) -> None:
    """Apply configured middleware to *app*."""
    if app.config.get("ENABLE_SECURITY_HEADERS", True):
        app.wsgi_app = security_headers_middleware(app.wsgi_app)  # type: ignore[assignment]
    if app.config.get("ENABLE_RATE_LIMITING", False):
        limit = int(app.config.get("RATE_LIMIT", 60))
        window = int(app.config.get("RATE_LIMIT_WINDOW", 60))
        app.wsgi_app = rate_limiting_middleware(app.wsgi_app, limit=limit, window=window)  # type: ignore[assignment]
    if app.config.get("ENABLE_INPUT_VALIDATION", True):
        app.wsgi_app = input_validation_middleware(app.wsgi_app)  # type: ignore[assignment]
    if app.config.get("ENABLE_SESSION_MANAGEMENT", True):
        app.wsgi_app = session_management_middleware(app.wsgi_app)  # type: ignore[assignment]


__all__ = [
    "init_app",
    "input_validation_middleware",
    "rate_limiting_middleware",
    "security_headers_middleware",
    "session_management_middleware",
]
