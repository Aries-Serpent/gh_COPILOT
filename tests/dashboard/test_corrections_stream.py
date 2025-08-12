import json
import sqlite3
import asyncio
from pathlib import Path

import websockets
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


def test_corrections_stream_live(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    app = Flask(__name__)
    app.add_url_rule("/corrections_stream", view_func=ed.corrections_stream)
    client = app.test_client()
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


def test_corrections_websocket(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)

    async def receive() -> list:
        await asyncio.sleep(0.1)
        uri = f"ws://localhost:{ed.CORRECTIONS_WS_PORT}/ws/corrections"
        async with websockets.connect(uri) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            return json.loads(msg)

    payload = asyncio.run(receive())
    assert payload[0]["path"] == "file1.py"
