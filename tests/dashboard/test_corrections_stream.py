import json
import queue
import sqlite3
from pathlib import Path

import dashboard.enterprise_dashboard as ed
from flask import Flask


def _create_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE correction_logs(timestamp TEXT, path TEXT, status TEXT)"
        )
        conn.execute(
            "INSERT INTO correction_logs VALUES (?,?,?)",
            ("2024-01-01", "file1.py", "pending"),
        )
        conn.commit()
    return db


def test_corrections_stream_once(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    app = Flask(__name__)
    app.add_url_rule("/corrections_stream", view_func=ed.corrections_stream)
    client = app.test_client()
    resp = client.get("/corrections_stream?once=1")
    assert resp.status_code == 200
    line = resp.data.decode().split("\n")[0]
    assert line.startswith("data:")
    logs = json.loads(line.split("data: ")[1])
    assert logs[0]["path"] == "file1.py"


def test_corrections_broadcast(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    q: "queue.Queue[str]" = queue.Queue()
    ed._sse_subscribers.append(q)

    class DummyWS:
        def __init__(self) -> None:
            self.sent: list[str] = []

        def send(self, msg: str) -> None:
            self.sent.append(msg)

    ws = DummyWS()
    ed._ws_clients.append(ws)
    try:
        ed._broadcast_corrections()
        sse_payload = json.loads(q.get(timeout=1))[0]
        ws_payload = json.loads(ws.sent[0])[0]
        assert sse_payload["path"] == "file1.py"
        assert ws_payload["path"] == "file1.py"
    finally:
        ed._sse_subscribers.remove(q)
        ed._ws_clients.remove(ws)

