import sqlite3
from pathlib import Path

from dashboard import enterprise_dashboard as ed
import dashboard.integrated_dashboard as idash


def test_violation_logs_endpoint(monkeypatch, tmp_path: Path):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE violation_logs (timestamp TEXT, details TEXT)"
        )
        conn.execute(
            "INSERT INTO violation_logs VALUES ('t', 'problem')"
        )
    monkeypatch.setattr(idash, "ANALYTICS_DB", db)
    client = ed.app.test_client()
    resp = client.get("/violations")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["violations"][0]["details"] == "problem"
