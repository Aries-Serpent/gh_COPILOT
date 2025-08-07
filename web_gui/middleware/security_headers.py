"""WSGI middleware for adding common security headers.

This module exposes :func:`security_headers_middleware` which can be used to
wrap a WSGI application (such as ``Flask.wsgi_app``) to inject security
headers into every response.
"""

from typing import Callable, Iterable, Tuple

from secondary_copilot_validator import SecondaryCopilotValidator

WSGIApp = Callable[[dict, Callable], Iterable[bytes]]


def security_headers_middleware(
    app: WSGIApp, validator: SecondaryCopilotValidator | None = None
) -> WSGIApp:
    """Wrap ``app`` to add security headers to each response."""

    validator = validator or SecondaryCopilotValidator()

    def middleware(environ: dict, start_response: Callable):  # type: ignore[override]
        def custom_start_response(
            status: str, headers: list[Tuple[str, str]], exc_info=None
        ) -> Callable:
            headers = list(headers)
            headers.extend(
                [
                    ("X-Content-Type-Options", "nosniff"),
                    ("X-Frame-Options", "DENY"),
                    ("Content-Security-Policy", "default-src 'self'"),
                ]
            )
            validator.validate_corrections([h[0] for h in headers])
            return start_response(status, headers, exc_info)

        return app(environ, custom_start_response)

    return middleware


__all__ = ["security_headers_middleware"]

