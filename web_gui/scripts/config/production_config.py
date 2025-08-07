"""Secure production configuration for the Web GUI.

This module enforces security-focused defaults for deployment.
Each setting includes rationale to aid future maintenance.
"""

from __future__ import annotations

# Disable debug mode to avoid exposing sensitive stack traces to users.
DEBUG = False

# Ensure session cookies are sent only over HTTPS to protect confidentiality.
SESSION_COOKIE_SECURE = True

# Prevent client-side scripts from accessing the session cookie.
SESSION_COOKIE_HTTPONLY = True

# Restrict cookies from being sent with cross-site requests, mitigating CSRF.
SESSION_COOKIE_SAMESITE = "Strict"

# Generate URLs with HTTPS by default to enforce encrypted connections.
PREFERRED_URL_SCHEME = "https"

# Enable CSRF protection to guard against cross-site request forgery attacks.
WTF_CSRF_ENABLED = True

# Ensure persistent login cookies are transmitted only over HTTPS.
REMEMBER_COOKIE_SECURE = True

# Prevent JavaScript from reading the persistent login cookie.
REMEMBER_COOKIE_HTTPONLY = True

# Apply strict same-site policy to persistent login cookies.
REMEMBER_COOKIE_SAMESITE = "Strict"
