import json
import time
from pathlib import Path

from flask import Flask, jsonify, request
import pytest

pytest.importorskip("pyotp")
import pyotp

from src.dashboard.auth import SessionManager
from src.dashboard import auth
from dashboard import compliance_metrics_updater as cmu


def create_app(summary_path: Path) -> Flask:
    app = Flask(__name__)
    manager = SessionManager.create()

    @app.post("/login")
    def login() -> any:
        token = request.json.get("token", "")
        mfa = request.json.get("mfa", "")
        session = manager.start_session(token, mfa)
        return jsonify({"session": session})

    @app.get("/corrections")
    def corrections() -> any:
        token = request.headers.get("X-Auth-Token", "")
        session = request.headers.get("X-Session-ID", "")
        if not manager.validate(token, session):
            return ("Unauthorized", 401)
        data = json.loads(summary_path.read_text())
        return jsonify(data)

    return app


def test_dashboard_workflow(monkeypatch, tmp_path: Path) -> None:
    secret = pyotp.random_base32()
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setenv("DASHBOARD_MFA_SECRET", secret)
    summary = tmp_path / "correction_summary.json"
    summary.write_text(json.dumps({"corrections": [{"file_path": "file.py"}]}))

    monkeypatch.setattr(cmu, "ANALYTICS_DB", tmp_path / "analytics.db")
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    time.sleep(0.2)

    app = create_app(summary)
    client = app.test_client()

    login_resp = client.post(
        "/login", json={"token": "secret", "mfa": pyotp.TOTP(secret).now()}
    )
    assert login_resp.status_code == 200
    session_id = login_resp.get_json()["session"]

    corr_resp = client.get(
        "/corrections",
        headers={"X-Auth-Token": "secret", "X-Session-ID": session_id},
    )
    assert corr_resp.status_code == 200
    assert corr_resp.get_json()["corrections"][0]["file_path"] == "file.py"

    unauthorized = client.get("/corrections")
    assert unauthorized.status_code == 401
