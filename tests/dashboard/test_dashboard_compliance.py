from pathlib import Path
import sqlite3
import sys
import types


def _setup_monitoring_stub(monkeypatch):
    stub = types.ModuleType("monitoring")

    class DummyDetector:
        threshold = 0.0

        def __init__(self, db_path=None):
            pass

        def zscores(self):
            return []

        def detect(self):
            return []

    setattr(stub, "BaselineAnomalyDetector", DummyDetector)
    sys.modules["monitoring"] = stub

    from flask import Flask

    idb = types.ModuleType("dashboard.integrated_dashboard")
    templates_path = Path(__file__).resolve().parents[2] / "dashboard" / "templates"
    app = Flask(__name__, template_folder=str(templates_path))
    idb.app = app
    idb._dashboard = app
    idb.create_app = lambda *_a, **_k: app
    idb._load_metrics = lambda *_a, **_k: {}
    idb.get_rollback_logs = lambda *_a, **_k: []
    idb._load_sync_events = lambda *_a, **_k: []
    idb.METRICS_FILE = Path("metrics.json")
    idb.ANALYTICS_DB = Path("analytics.db")

    def _payload() -> dict:
        with sqlite3.connect(idb.ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM todo_fixme_tracking WHERE status='open'"
            )
            placeholders_open = cur.fetchone()[0]
            cur = conn.execute(
                "SELECT resolved_timestamp FROM todo_fixme_tracking WHERE resolved_timestamp IS NOT NULL ORDER BY resolved_timestamp DESC LIMIT 1"
            )
            row = cur.fetchone()
            last_resolved = row[0] if row and row[0] else ""
            cur = conn.execute(
                "SELECT summary, ts FROM code_audit_log ORDER BY ts DESC LIMIT 20"
            )
            audit_log = [{"summary": r[0], "ts": r[1]} for r in cur.fetchall()]
        return {
            "placeholders_open": placeholders_open,
            "last_resolved": last_resolved,
            "audit_log": audit_log,
        }

    idb._compliance_payload = _payload
    idb._load_compliance_payload = _payload
    idb.validate_enterprise_operation = lambda *_a, **_k: True
    monkeypatch.setitem(sys.modules, "dashboard.integrated_dashboard", idb)


def _prepare_db(tmp_path):
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
    return db


def test_dashboard_compliance_endpoint(tmp_path, monkeypatch):
    _setup_monitoring_stub(monkeypatch)
    import dashboard.enterprise_dashboard as ed
    import dashboard.integrated_dashboard as idb

    db = _prepare_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(idb, "ANALYTICS_DB", db)
    monkeypatch.setattr(idb, "validate_enterprise_operation", lambda *_a, **_k: True)
    client = ed.app.test_client()
    resp = client.get("/api/dashboard/compliance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["placeholders_open"] == 1
    assert any(e["summary"] == "fixed file" for e in data["audit_log"])
    assert any(entry["file_path"] == "a.py" for entry in data["todo_entries"])
