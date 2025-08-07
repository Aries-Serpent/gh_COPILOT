"""Basic token-based authentication utilities."""

from __future__ import annotations

from flask import Flask, Response, request


def init_app(app: Flask) -> None:
    """Register a simple authentication check on *app*.

    The check is enabled when ``AUTH_REQUIRED`` is ``True``. Incoming requests
    must include an ``Authorization`` header matching ``Bearer <AUTH_TOKEN>``.
    """
    app.config.setdefault("AUTH_REQUIRED", False)
    app.config.setdefault("AUTH_TOKEN", "")

    if not app.config["AUTH_REQUIRED"]:
        return

    @app.before_request
    def _verify_auth() -> Response | None:
        token = app.config.get("AUTH_TOKEN", "")
        header = request.headers.get("Authorization", "")
        if header != f"Bearer {token}":
            return Response("Unauthorized", status=401)
        return None


__all__ = ["init_app"]
