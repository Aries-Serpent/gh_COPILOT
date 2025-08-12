import sqlite3
import sys
import types


def test_dashboard_compliance_endpoint(tmp_path, monkeypatch):
    stub = types.ModuleType("monitoring")
    class DummyDetector:
        threshold = 0.0
        def __init__(self, db_path=None):
            pass
        def zscores(self):
            return []
        def detect(self):
            return []
    stub.BaselineAnomalyDetector = DummyDetector
    sys.modules["monitoring"] = stub

    import dashboard.enterprise_dashboard as ed
    import dashboard.integrated_dashboard as idb

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
    monkeypatch.setattr(idb, "ANALYTICS_DB", db)
    monkeypatch.setattr(idb, "validate_enterprise_operation", lambda *_a, **_k: True)
    client = ed.app.test_client()
    resp = client.get("/dashboard/compliance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["placeholders_open"] == 1
    assert any(e["summary"] == "fixed file" for e in data["audit_log"])

