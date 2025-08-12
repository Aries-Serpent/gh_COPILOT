import pytest
import sqlite3

from flask import Flask

from src.dashboard import auth
from src.dashboard.api import logs as logs_api


@pytest.fixture(autouse=True)
def _mock_mfa(monkeypatch):
    monkeypatch.setattr(auth, "_check_mfa", lambda *_: None)


@pytest.fixture()
def manager() -> auth.SessionManager:
    return auth.SessionManager.create(max_attempts=3)


def test_bruteforce_protection(monkeypatch, manager) -> None:
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    for _ in range(manager.max_attempts):
        with pytest.raises(ValueError):
            manager.start_session("bad", "")
    with pytest.raises(ValueError):
        manager.start_session("secret", "")
    now = auth.time.time()
    monkeypatch.setattr(auth.time, "time", lambda: now + 61)
    session = manager.start_session("secret", "")
    assert manager.validate("secret", session)


def test_csrf_and_auth(monkeypatch, manager, tmp_path) -> None:
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setattr(auth, "SESSION_MANAGER", manager)

    db_path = tmp_path / "analytics.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE correction_logs(timestamp TEXT, path TEXT, status TEXT)"
        )

    app = Flask(__name__)
    monkeypatch.setattr(logs_api, "ANALYTICS_DB", db_path)
    app.register_blueprint(logs_api.bp)

    @app.route("/needs-csrf", methods=["POST"])
    @auth.require_session(manager)
    def needs_csrf() -> str:
        return "ok"

    client = app.test_client()
    session_id = manager.start_session("secret", "")
    csrf = manager.get_csrf_token(session_id)

    assert client.get("/correction-logs").status_code == 401
    headers = {"X-Auth-Token": "secret", "X-Session-Id": session_id}
    assert client.get("/correction-logs", headers=headers).status_code == 200

    assert client.post("/needs-csrf", headers=headers).status_code == 403
    headers["X-CSRF-Token"] = csrf
    assert client.post("/needs-csrf", headers=headers).status_code == 200

