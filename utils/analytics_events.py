from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(os.getenv("ANALYTICS_DB_PATH", "databases/analytics.db"))


def _insert_direct(run_id: str, kind: str, payload: str, ts: Optional[str]) -> bool:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        if ts is None:
            cur.execute(
                "INSERT INTO analytics_events(run_id, kind, payload) VALUES (?, ?, ?)",
                (run_id, kind, payload),
            )
        else:
            cur.execute(
                "INSERT INTO analytics_events(run_id, kind, payload, ts) VALUES (?, ?, ?, ?)",
                (run_id, kind, payload, ts),
            )
        con.commit()
        return True
    finally:
        con.close()


def log_analytics_event(run_id: str, kind: str, payload: Any, ts: Optional[str] = None) -> bool:
    """Log an event into the analytics_events table.

    Attempts to delegate to utils.log_utils._log_event. Falls back to a direct
    sqlite3 insert if the helper is unavailable.
    """
    if isinstance(payload, (dict, list)):
        payload = json.dumps(payload, separators=(",", ":"))
    else:
        payload = str(payload)

    try:
        from utils.log_utils import _log_event  # type: ignore
        record = {"run_id": run_id, "kind": kind, "payload": payload, "ts": ts}
        return bool(_log_event(record, table="analytics_events", db_path=DB_PATH))
    except Exception:
        return _insert_direct(run_id, kind, payload, ts)
