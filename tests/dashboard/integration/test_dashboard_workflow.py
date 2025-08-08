import asyncio
import json
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, request

from src.dashboard.auth import SessionManager
from dashboard import compliance_metrics_updater as cmu


def create_app(summary_path: Path) -> Flask:
    app = Flask(__name__)
    manager = SessionManager.create()

    @app.post("/login")
    def login() -> any:
        token = request.json.get("token", "")
        session = manager.start_session(token)
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


async def _receive_ws(updater: cmu.ComplianceMetricsUpdater) -> dict:
    import websockets

    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        threading.Timer(
            0.2, lambda: updater._log_update_event({"value": 7}, test_mode=True)
        ).start()
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        return json.loads(msg)


def test_dashboard_workflow(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DASHBOARD_AUTH_TOKEN", "secret")
    monkeypatch.setenv("LOG_WEBSOCKET_ENABLED", "1")
    summary = tmp_path / "correction_summary.json"
    summary.write_text(json.dumps({"corrections": [{"file_path": "file.py"}]}))

    monkeypatch.setattr(cmu, "ANALYTICS_DB", tmp_path / "analytics.db")
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    time.sleep(0.2)

    app = create_app(summary)
    client = app.test_client()

    login_resp = client.post("/login", json={"token": "secret"})
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

    payload = asyncio.run(_receive_ws(updater))
    assert payload["value"] == 7
