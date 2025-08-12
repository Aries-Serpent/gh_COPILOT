import sqlite3

import dashboard.enterprise_dashboard as ed
import dashboard.integrated_dashboard as idash


def test_dashboard_compliance_endpoint(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (file_path TEXT, line_number INTEGER, placeholder_type TEXT, status TEXT, resolved_timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES ('a.py',1,'TODO','open',NULL)"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES ('b.py',2,'FIXME','resolved','2024-01-01')"
        )
        conn.execute("CREATE TABLE code_audit_log (summary TEXT, ts TEXT)")
        conn.execute("INSERT INTO code_audit_log VALUES ('fixed file', '2024-01-02')")
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(idash, "ANALYTICS_DB", db)
    monkeypatch.setattr(idash, "validate_enterprise_operation", lambda *_a, **_k: True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    client = ed.app.test_client()
    resp = client.get("/api/dashboard/compliance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["open_placeholders"] == 1
    assert any(log["summary"] == "fixed file" for log in data["code_audit_log"])

