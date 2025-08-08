import asyncio
import json
import threading
import time
from pathlib import Path

from dashboard import compliance_metrics_updater as cmu


def test_websocket_metrics_broadcast(monkeypatch, tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    monkeypatch.setenv("LOG_WEBSOCKET_ENABLED", "1")
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)

    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    time.sleep(0.2)

    async def receive() -> dict:
        import websockets

        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as ws:
            threading.Timer(
                0.2,
                lambda: updater._log_update_event({"value": 1}, test_mode=True),
            ).start()
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            return json.loads(msg)

    payload = asyncio.run(receive())
    assert payload["value"] == 1
