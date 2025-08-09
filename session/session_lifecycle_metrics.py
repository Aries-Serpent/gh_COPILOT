"""Session lifecycle metric helpers."""
from __future__ import annotations

from pathlib import Path
import os, sqlite3, time
from typing import Optional

__all__ = ["start_session", "end_session"]


def _db(workspace: Optional[str] = None) -> Path:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    return ws / "databases" / "analytics.db"


def _ensure(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS session_lifecycle (session_id TEXT PRIMARY KEY, start_ts INTEGER NOT NULL, end_ts INTEGER, duration_seconds REAL, zero_byte_violations INTEGER DEFAULT 0, recursion_flags INTEGER DEFAULT 0, status TEXT DEFAULT 'running')""")


def start_session(session_id: str, *, workspace: Optional[str] = None) -> None:
    db_path = _db(workspace)
    if not db_path.exists():  # pragma: no cover
        return
    with sqlite3.connect(db_path) as conn:
        _ensure(conn)
        conn.execute("INSERT OR REPLACE INTO session_lifecycle(session_id, start_ts, status) VALUES(?,?,'running')", (session_id, int(time.time())))
        conn.commit()


def end_session(session_id: str, *, zero_byte_violations: int = 0, recursion_flags: int = 0, status: str = "success", workspace: Optional[str] = None) -> None:
    db_path = _db(workspace)
    if not db_path.exists():  # pragma: no cover
        return
    with sqlite3.connect(db_path) as conn:
        _ensure(conn)
        cur = conn.execute("SELECT start_ts FROM session_lifecycle WHERE session_id=?", (session_id,))
        row = cur.fetchone()
        start_ts = row[0] if row else int(time.time())
        end_ts = int(time.time())
        duration = end_ts - start_ts
        conn.execute("UPDATE session_lifecycle SET end_ts=?, duration_seconds=?, zero_byte_violations=?, recursion_flags=?, status=? WHERE session_id=?", (end_ts, float(duration), int(zero_byte_violations), int(recursion_flags), status, session_id))
        conn.commit()
