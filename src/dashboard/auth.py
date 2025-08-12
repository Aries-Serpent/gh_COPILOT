from __future__ import annotations

"""Simple token and session validation utilities for the dashboard."""

from dataclasses import dataclass
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

# In-memory rate limit storage: {identifier: [timestamp, ...]}
_RATE_LIMIT: Dict[str, List[float]] = {}


@dataclass
class _Session:
    """Internal representation of a session."""

    csrf: str
    expires_at: float


def _check_rate_limit(identifier: str = "global", limit: int = 5, window: int = 60) -> None:
    """Simple in-memory rate limiting.

    Parameters
    ----------
    identifier:
        Unique identifier for a client or session.
    limit:
        Maximum number of calls allowed within the window.
    window:
        Time window in seconds.
    """
    now = time.time()
    events = _RATE_LIMIT.setdefault(identifier, [])
    events = [ts for ts in events if now - ts < window]
    if len(events) >= limit:
        raise ValueError("Too many requests")
    events.append(now)
    _RATE_LIMIT[identifier] = events


def _check_mfa(token: str | None) -> None:
    """Validate a user-provided TOTP code.

    Parameters
    ----------
    token:
        The one-time password supplied by the user.  The secret used to
        validate the token is read from ``DASHBOARD_MFA_SECRET``.
    """

    if token is None:
        raise ValueError("MFA token required")

    secret = os.environ.get("DASHBOARD_MFA_SECRET")
    if not secret:
        raise ValueError("MFA secret not configured")

    try:  # pragma: no cover - optional dependency
        import pyotp
    except Exception as exc:  # pragma: no cover - dependency issue
        raise ValueError("pyotp library is required for MFA") from exc

    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        raise ValueError("Invalid MFA token")


@dataclass
class SessionManager:
    """Manage in-memory sessions for the dashboard."""

    active_sessions: Dict[str, _Session]
    failed_attempts: int = 0
    max_attempts: int = 5
    session_timeout: int = 3600
    lock_until: float = 0.0

    @classmethod
    def create(cls, max_attempts: int = 5, session_timeout: int = 3600) -> "SessionManager":
        return cls(
            active_sessions={},
            failed_attempts=0,
            max_attempts=max_attempts,
            session_timeout=session_timeout,
        )

    def start_session(self, token: str, mfa_token: str | None = None) -> str:
        """Start a session if both auth token and MFA code are valid."""

        _check_rate_limit("start_session")
        now = time.time()
        if now < self.lock_until:
            raise ValueError("Too many failed attempts")
        expected = os.environ.get("DASHBOARD_AUTH_TOKEN", "")
        if not hmac.compare_digest(token, expected):
            self.failed_attempts += 1
            if self.failed_attempts >= self.max_attempts:
                self.lock_until = now + 60
                raise ValueError("Too many failed attempts")
            raise ValueError("Invalid token")
        self.failed_attempts = 0
        self.lock_until = 0
        _check_mfa(mfa_token)
        session_id = str(uuid.uuid4())
        csrf_token = secrets.token_hex(16)
        self.active_sessions[session_id] = _Session(
            csrf=csrf_token, expires_at=now + self.session_timeout
        )
        return session_id

    def refresh_session(self, token: str, session_id: str) -> str:
        """Refresh an existing session and return a new session id."""

        if not self.validate(token, session_id):
            raise ValueError("Invalid session")
        new_id = str(uuid.uuid4())
        csrf_token = secrets.token_hex(16)
        now = time.time()
        self.active_sessions[new_id] = _Session(
            csrf=csrf_token, expires_at=now + self.session_timeout
        )
        self.end_session(session_id)
        return new_id

    def get_csrf_token(self, session_id: str) -> Optional[str]:
        """Return the CSRF token for a given session."""

        info = self.active_sessions.get(session_id)
        return info.csrf if info else None

    def validate(self, token: str, session_id: str) -> bool:
        """Return True if token and session identifier are valid."""

        expected = os.environ.get("DASHBOARD_AUTH_TOKEN", "")
        if not hmac.compare_digest(token, expected):
            return False
        info = self.active_sessions.get(session_id)
        if not info:
            return False
        if info.expires_at < time.time():
            self.end_session(session_id)
            return False
        return True

    def end_session(self, session_id: str) -> None:
        """Remove a session identifier from the active set."""

        self.active_sessions.pop(session_id, None)


SESSION_MANAGER = SessionManager.create()


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def generate_jwt(payload: Dict[str, Any], secret: str, expires_in: int = 3600) -> str:
    """Return a signed JWT for the given payload."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = payload.copy()
    payload["exp"] = int(time.time()) + expires_in
    header_b64 = _b64encode(json.dumps(header).encode())
    payload_b64 = _b64encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).hexdigest()
    return f"{header_b64}.{payload_b64}.{signature}"


def decode_jwt(token: str, secret: str) -> Dict[str, Any]:
    """Decode and validate a signed JWT."""
    try:
        header_b64, payload_b64, signature = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            raise ValueError("Invalid signature")
        payload = json.loads(_b64decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        return payload
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid token") from exc


def verify_token_and_session(token: str, session_id: str, manager: SessionManager | None = None) -> bool:
    """Return True if the provided token and session are valid."""
    mgr = manager or SESSION_MANAGER
    return mgr.validate(token, session_id)


def require_session(manager: SessionManager | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator enforcing session and CSRF checks on Flask routes."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from flask import abort, request

            mgr = manager or SESSION_MANAGER
            expected = os.environ.get("DASHBOARD_AUTH_TOKEN")
            if expected:
                token = request.headers.get("X-Auth-Token", "")
                session_id = request.headers.get("X-Session-Id", "")
                _check_rate_limit(f"session:{session_id}")
                if not mgr.validate(token, session_id):
                    abort(401)
                if request.method not in {"GET", "HEAD", "OPTIONS"}:
                    csrf = request.headers.get("X-CSRF-Token", "")
                    if mgr.get_csrf_token(session_id) != csrf:
                        abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
