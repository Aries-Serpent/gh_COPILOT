from flask import Flask, jsonify, request

import pytest

pytest.importorskip("pyotp")
import pyotp

from src.dashboard.auth import SessionManager
from src.dashboard import auth


def create_app() -> Flask:
    app = Flask(__name__)
    manager = SessionManager.create()

    @app.post("/login")
    def login() -> any:
        token = request.json.get("token", "")
        mfa = request.json.get("mfa", "")
        session = manager.start_session(token, mfa)
        return jsonify({"session": session})

    @app.get("/protected")
    def protected() -> any:
        token = request.headers.get("X-Auth-Token", "")
        session = request.headers.get("X-Session-ID", "")
        if manager.validate(token, session):
            return jsonify({"ok": True})
        return ("Unauthorized", 401)

    @app.post("/logout")
    def logout() -> any:
        session = request.json.get("session", "")
        manager.end_session(session)
        return ("", 204)

    return app


def test_auth_end_to_end(monkeypatch):
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setattr(auth, "_check_mfa", lambda *_: None)
    app = create_app()
    client = app.test_client()

    login_resp = client.post(
        "/login", json={"token": "secret", "mfa": pyotp.TOTP(secret).now()}
    )
    assert login_resp.status_code == 200
    session = login_resp.get_json()["session"]

    ok_resp = client.get(
        "/protected",
        headers={"X-Auth-Token": "secret", "X-Session-ID": session},
    )
    assert ok_resp.status_code == 200

    logout_resp = client.post("/logout", json={"session": session})
    assert logout_resp.status_code == 204

    fail_resp = client.get(
        "/protected",
        headers={"X-Auth-Token": "secret", "X-Session-ID": session},
    )
    assert fail_resp.status_code == 401
