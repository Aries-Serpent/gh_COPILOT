"""Simple in-memory rate limiting WSGI middleware."""

from __future__ import annotations

import time
from typing import Callable, Dict, Iterable

WSGIApp = Callable[[dict, Callable], Iterable[bytes]]


def rate_limiting_middleware(app: WSGIApp, limit: int = 60, window: int = 60) -> WSGIApp:
    """Wrap ``app`` with a naive IP-based rate limiter."""

    hits: Dict[str, list[float]] = {}

    def middleware(environ: dict, start_response: Callable):  # type: ignore[override]
        addr = environ.get("REMOTE_ADDR", "unknown")
        now = time.time()
        records = [t for t in hits.get(addr, []) if now - t < window]
        if len(records) >= limit:
            start_response("429 Too Many Requests", [("Content-Type", "text/plain")])
            return [b"Rate limit exceeded"]
        records.append(now)
        hits[addr] = records
        return app(environ, start_response)

    return middleware


__all__ = ["rate_limiting_middleware"]

