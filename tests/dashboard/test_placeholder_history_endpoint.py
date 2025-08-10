import sqlite3

import dashboard.enterprise_dashboard as ed


def test_placeholder_history_endpoint(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE placeholder_audit_snapshots (timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit_snapshots VALUES (1, 2, 3)"
        )
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)

    client = ed.app.test_client()
    resp = client.get("/api/placeholder_history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["history"][0]["open"] == 2
