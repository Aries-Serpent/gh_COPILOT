import sqlite3
from pathlib import Path

import dashboard.enterprise_dashboard as ed


def test_dashboard_compliance_endpoint(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (status TEXT, resolved_timestamp TEXT)"
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('open', NULL)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('resolved', '2024-01-01')")
        conn.execute("CREATE TABLE code_audit_log (summary TEXT, ts TEXT)")
        conn.execute("INSERT INTO code_audit_log VALUES ('fixed file', '2024-01-02')")
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(ed, "validate_enterprise_operation", lambda *_a, **_k: True)
    client = ed.app.test_client()
    resp = client.get("/dashboard/compliance")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Open placeholders: 1" in text
    assert "fixed file" in text

