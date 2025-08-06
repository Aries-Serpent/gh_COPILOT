import asyncio
import json
import threading
from pathlib import Path
import time

from dashboard import compliance_metrics_updater as cmu
from dashboard import enterprise_dashboard as ed


def test_metrics_endpoint(monkeypatch):
    monkeypatch.setattr(
        ed,
        "_load_metrics",
        lambda: {"metrics": {"composite_score": 0.9, "recursion_status": "clear"}},
    )
    client = ed.app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["metrics"]["composite_score"] == 0.9
    assert data["metrics"]["recursion_status"] == "clear"


def test_websocket_broadcast(monkeypatch, tmp_path: Path):
    db = tmp_path / "analytics.db"
    monkeypatch.setenv("LOG_WEBSOCKET_ENABLED", "1")
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)

    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    time.sleep(0.2)

    async def receive() -> str:
        import websockets

        uri = "ws://localhost:8765"

        async with websockets.connect(uri) as ws:
            threading.Timer(
                0.2,
                lambda: updater._log_update_event(
                    {"composite_score": 0.5}, test_mode=True
                ),
            ).start()
            return await asyncio.wait_for(ws.recv(), timeout=5)

    message = asyncio.run(receive())
    payload = json.loads(message)
    assert payload["composite_score"] == 0.5
