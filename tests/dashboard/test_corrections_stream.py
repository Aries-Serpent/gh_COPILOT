import json
import sqlite3
from pathlib import Path

import dashboard.enterprise_dashboard as ed


def _create_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE correction_logs(timestamp TEXT, path TEXT, status TEXT)"
        )
        conn.execute(
            "INSERT INTO correction_logs VALUES ('t1', 'file1.py', 'fixed')"
        )
    return db


def test_corrections_stream_once(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    client = ed.app.test_client()
    resp = client.get("/corrections_stream?once=1")
    assert resp.status_code == 200
    line = resp.data.decode().split("\n")[0]
    assert line.startswith("data:")
    logs = json.loads(line.split("data: ")[1])
    assert logs[0]["path"] == "file1.py"


def test_corrections_stream_live(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    client = ed.app.test_client()
    resp = client.get("/corrections_stream?interval=0", buffered=False)
    first = next(resp.response).decode().strip()
    assert first.startswith("data:")
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO correction_logs VALUES ('t2', 'file2.py', 'pending')"
        )
    second = next(resp.response).decode().strip()
    data = json.loads(second.split("data: ")[1])
    assert any(entry["path"] == "file2.py" for entry in data)

