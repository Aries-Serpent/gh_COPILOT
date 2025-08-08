"""Tests for web GUI middleware modules."""

from flask import Flask, session

from secondary_copilot_validator import SecondaryCopilotValidator

from web_gui.middleware import (
    input_validation,
    rate_limiting,
    security_headers,
    session_management,
)
from web_gui import middleware


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "test"

    @app.route("/")
    def index():
        session["foo"] = "bar"
        return "OK"

    return app


def test_security_headers() -> None:
    app = create_app()
    app.wsgi_app = security_headers.security_headers_middleware(app.wsgi_app)
    client = app.test_client()
    resp = client.get("/")
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"


def test_rate_limiting() -> None:
    app = create_app()
    app.wsgi_app = rate_limiting.rate_limiting_middleware(app.wsgi_app, limit=1, window=60)
    client = app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 429


def test_input_validation() -> None:
    app = create_app()
    app.wsgi_app = input_validation.input_validation_middleware(app.wsgi_app)
    client = app.test_client()
    assert client.get("/?q=test").status_code == 200
    assert client.get("/?q=<script>").status_code == 400


def test_session_management() -> None:
    app = create_app()
    app.wsgi_app = session_management.session_management_middleware(app.wsgi_app)
    client = app.test_client()
    resp = client.get("/")
    cookie = resp.headers["Set-Cookie"]
    assert "Secure" in cookie and "HttpOnly" in cookie


def test_middleware_dual_copilot(monkeypatch) -> None:
    app = create_app()
    validator = SecondaryCopilotValidator()
    calls: list[list[object]] = []
    monkeypatch.setattr(
        validator, "validate_corrections", lambda items, primary_success=True: calls.append(items) or True
    )
    app.wsgi_app = security_headers.security_headers_middleware(app.wsgi_app, validator=validator)
    client = app.test_client()
    client.get("/")
    assert calls


def test_init_app_applies_middlewares() -> None:
    app = create_app()
    app.config.update({"ENABLE_RATE_LIMITING": False})
    middleware.init_app(app)
    client = app.test_client()
    resp = client.get("/")
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert client.get("/?q=<script>").status_code == 400

