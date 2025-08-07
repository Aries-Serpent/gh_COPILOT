"""Request audit logging utilities."""

from __future__ import annotations

from flask import Flask, Response, request


def init_app(app: Flask) -> None:
    """Log each request and response status code when enabled."""
    app.config.setdefault("AUDIT_LOGGING", False)

    if not app.config["AUDIT_LOGGING"]:
        return

    @app.after_request
    def _log_response(response: Response) -> Response:
        app.logger.info("AUDIT %s %s -> %s", request.method, request.path, response.status_code)
        return response


__all__ = ["init_app"]
