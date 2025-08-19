import os
import sqlite3
import tempfile
import datetime as dt
from pathlib import Path
from tools.apply_analytics_event_workflow import log_analytics_event


def test_log_analytics_event_inserts_one_row():
    # Use a temp on-disk file to allow PRAGMAs, but not the real analytics.db
    with tempfile.TemporaryDirectory() as td:
        dbp = Path(td) / "tmp_analytics.db"
        os.environ.pop("ALLOW_DB_MIGRATIONS", None)  # keep explicit control
        # Create table explicitly for on-disk temp DB
        conn = sqlite3.connect(str(dbp))
        try:
            conn.execute("""
                CREATE TABLE analytics_events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    ts TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

        rid = "RUN-UNITTEST-001"
        kind = "sample"
        payload = {"ok": True}
        ts = dt.datetime(2025, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

        last_id = log_analytics_event(rid, kind, payload, ts, db_path=dbp)
        assert isinstance(last_id, int) and last_id >= 1

        conn = sqlite3.connect(str(dbp))
        try:
            cur = conn.execute("SELECT run_id, kind, payload, ts FROM analytics_events")
            rows = cur.fetchall()
            assert len(rows) == 1
            r = rows[0]
            assert r[0] == rid
            assert r[1] == kind
            assert '"ok":true' in r[2]
            assert r[3].endswith("Z")
        finally:
            conn.close()
