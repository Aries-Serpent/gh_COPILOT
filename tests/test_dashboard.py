import asyncio
import json
import sqlite3
import threading
from pathlib import Path
import time

from dashboard import compliance_metrics_updater as cmu
from dashboard import enterprise_dashboard as ed
import dashboard.integrated_dashboard as idash


def test_metrics_endpoint(monkeypatch):
    monkeypatch.setattr(
        idash,
        "_load_metrics",
        lambda: {"composite_score": 0.9, "recursion_status": "clear"},
    )
    monkeypatch.setattr(
        idash,
        "_load_placeholder_history",
        lambda: [{"date": "2024-01-01", "count": 1}],
    )
    client = ed.app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["metrics"]["composite_score"] == 0.9
    assert data["metrics"]["recursion_status"] == "clear"
    assert data["placeholder_history"][0]["count"] == 1


def test_metrics_stream_history(monkeypatch):
    monkeypatch.setattr(idash, "_load_metrics", lambda: {"placeholder_removal": 1})
    monkeypatch.setattr(
        idash,
        "_load_placeholder_history",
        lambda: [{"date": "2024-01-01", "count": 1}],
    )
    client = ed.app.test_client()
    resp = client.get("/metrics_stream?once=1")
    line = resp.data.decode().split("\n")[0]
    payload = json.loads(line.split("data: ")[1])
    assert payload["placeholder_history"][0]["count"] == 1


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


def test_new_routes_and_dashboard_page(monkeypatch):
    monkeypatch.setattr(ed, "_load_sync_events", lambda: [
        {"timestamp": "t", "source_db": "a", "target_db": "b", "action": "sync"}
    ])
    monkeypatch.setattr(
        ed,
        "_load_audit_results",
        lambda: [{"placeholder_type": "TODO", "count": 1}],
    )
    monkeypatch.setattr(ed, "_load_corrections", lambda: [])
    monkeypatch.setattr(idash, "_load_metrics", lambda: {})
    monkeypatch.setattr(idash, "get_rollback_logs", lambda: [])
    monkeypatch.setattr(idash, "_load_sync_events", lambda: [])
    monkeypatch.setattr(idash, "_load_audit_results", lambda: [])
    client = ed.app.test_client()
    resp_sync = client.get("/sync_events")
    assert resp_sync.get_json()[0]["action"] == "sync"
    resp_audit = client.get("/audit_results")
    assert resp_audit.get_json()[0]["placeholder_type"] == "TODO"
    page = client.get("/").get_data(as_text=True)
    assert '<ul id="sync_events">' in page
    assert '<ul id="audit_results">' in page


def test_placeholder_history_reads_snapshots(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE placeholder_audit_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit_snapshots(timestamp, open_count, resolved_count) VALUES (?,?,?)",
            (int(time.time()), 5, 0),
        )
    monkeypatch.setattr(idash, "ANALYTICS_DB", db)
    history = idash._load_placeholder_history()
    assert history and history[0]["count"] == 5
