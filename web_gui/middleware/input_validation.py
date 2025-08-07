"""Basic input validation middleware."""

from __future__ import annotations

import re
from typing import Callable, Iterable

from secondary_copilot_validator import SecondaryCopilotValidator

WSGIApp = Callable[[dict, Callable], Iterable[bytes]]
SCRIPT_RE = re.compile(r"<script", re.IGNORECASE)


def input_validation_middleware(
    app: WSGIApp, validator: SecondaryCopilotValidator | None = None
) -> WSGIApp:
    """Reject requests containing obvious script tags in the query string."""

    validator = validator or SecondaryCopilotValidator()

    def middleware(environ: dict, start_response: Callable):  # type: ignore[override]
        query = environ.get("QUERY_STRING", "")
        if SCRIPT_RE.search(query):
            start_response("400 Bad Request", [("Content-Type", "text/plain")])
            validator.validate_corrections([query, "400"])
            return [b"Invalid input"]
        validator.validate_corrections([query])
        return app(environ, start_response)

    return middleware


__all__ = ["input_validation_middleware"]

