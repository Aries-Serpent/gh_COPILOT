import json
import os
import sqlite3
from pathlib import Path


def test_log_analytics_event_roundtrip(tmp_path):
    db = tmp_path / "analytics.db"
    os.environ["ANALYTICS_DB_PATH"] = str(db)

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS analytics_events (
          run_id  TEXT NOT NULL,
          kind    TEXT NOT NULL,
          payload TEXT NOT NULL,
          ts      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        );
        """
    )
    con.commit()
    con.close()

    from utils.analytics_events import log_analytics_event

    ok = log_analytics_event("RUN_TEST", "unit", {"ok": True}, "2025-08-18T00:00:00Z")
    assert ok

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute(
        "SELECT run_id, kind, payload, ts FROM analytics_events WHERE run_id=? AND kind=?",
        ("RUN_TEST", "unit"),
    )
    row = cur.fetchone()
    con.close()

    assert row is not None
    assert row[0] == "RUN_TEST"
    assert row[1] == "unit"
    data = json.loads(row[2])
    assert data.get("ok") is True
