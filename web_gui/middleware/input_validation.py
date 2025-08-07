"""Basic input validation middleware."""

from __future__ import annotations

import re
from typing import Callable, Iterable

WSGIApp = Callable[[dict, Callable], Iterable[bytes]]
SCRIPT_RE = re.compile(r"<script", re.IGNORECASE)


def input_validation_middleware(app: WSGIApp) -> WSGIApp:
    """Reject requests containing obvious script tags in the query string."""

    def middleware(environ: dict, start_response: Callable):  # type: ignore[override]
        query = environ.get("QUERY_STRING", "")
        if SCRIPT_RE.search(query):
            start_response("400 Bad Request", [("Content-Type", "text/plain")])
            return [b"Invalid input"]
        return app(environ, start_response)

    return middleware


__all__ = ["input_validation_middleware"]

