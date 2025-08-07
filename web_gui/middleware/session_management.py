"""Session management middleware."""

from __future__ import annotations

from typing import Callable, Iterable, Tuple

from secondary_copilot_validator import SecondaryCopilotValidator

WSGIApp = Callable[[dict, Callable], Iterable[bytes]]


def session_management_middleware(
    app: WSGIApp, validator: SecondaryCopilotValidator | None = None
) -> WSGIApp:
    """Ensure session cookies are marked secure and HTTP only."""

    validator = validator or SecondaryCopilotValidator()

    def middleware(environ: dict, start_response: Callable):  # type: ignore[override]
        def custom_start_response(
            status: str, headers: list[Tuple[str, str]], exc_info=None
        ) -> Callable:
            new_headers: list[Tuple[str, str]] = []
            for header, value in headers:
                if header.lower() == "set-cookie" and "session=" in value.lower():
                    if "httponly" not in value.lower():
                        value += "; HttpOnly"
                    if "secure" not in value.lower():
                        value += "; Secure"
                new_headers.append((header, value))
            validator.validate_corrections([h[0] for h in new_headers])
            return start_response(status, new_headers, exc_info)

        return app(environ, custom_start_response)

    return middleware


__all__ = ["session_management_middleware"]

