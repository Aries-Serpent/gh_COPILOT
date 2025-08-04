"""Tests for sync events routes in :mod:`dashboard.enterprise_dashboard`."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import dashboard.enterprise_dashboard as ed


def _setup_analytics_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE synchronization_events (timestamp INTEGER, source_db TEXT, target_db TEXT, action TEXT)"
        )
        conn.execute(
            "INSERT INTO synchronization_events (timestamp, source_db, target_db, action) VALUES (1, 'a.db', 'b.db', 'sync')"
        )
        conn.commit()


def test_sync_events_json_and_view(tmp_path, monkeypatch):
    analytics = tmp_path / "analytics.db"
    _setup_analytics_db(analytics)
    monkeypatch.setattr(ed, "ANALYTICS_DB", analytics)

    client = ed.app.test_client()
    resp = client.get("/sync-events")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["action"] == "sync"

    resp = client.get("/sync-events/view")
    assert resp.status_code == 200
    assert b"Synchronization Events" in resp.data
