"""Production configuration with security-focused defaults."""
from __future__ import annotations

import os

DEBUG = False
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change_me")
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
DATABASE_URI = "sqlite:///production.db"
