"""Tests for web GUI middleware modules."""

from flask import Flask, session

from web_gui.middleware import (
    input_validation,
    rate_limiting,
    security_headers,
    session_management,
)


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

