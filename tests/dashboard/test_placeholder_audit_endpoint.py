import sqlite3

import dashboard.enterprise_dashboard as ed


def test_placeholder_audit_endpoint(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE placeholder_audit_snapshots (timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
        )
        conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, 5, 3)")
        conn.execute(
            "CREATE TABLE placeholder_audit (id INTEGER PRIMARY KEY, file_path TEXT, line_number INTEGER, placeholder_type TEXT, context TEXT)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit (file_path, line_number, placeholder_type, context) VALUES ('file.py', 10, 'TODO', 'fix this')"
        )
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)

    client = ed.app.test_client()
    resp = client.get("/api/placeholder_audit")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["history"][0]["open"] == 5
    assert data["totals"]["open"] == 5
    assert data["totals"]["resolved"] == 3
    assert data["unresolved"][0]["type"] == "TODO"
