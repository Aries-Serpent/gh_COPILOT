"""Session lifecycle metric helpers."""

from __future__ import annotations

from pathlib import Path
import math
import os
import sqlite3
import time
from typing import Callable, Optional

__all__ = ["start_session", "end_session", "record_latency", "record_retry"]


def _db(workspace: Optional[str] = None) -> Path:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    return ws / "databases" / "production.db"


def _ensure(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS session_lifecycle
            (session_id TEXT PRIMARY KEY, start_ts INTEGER NOT NULL,
             end_ts INTEGER, duration_seconds REAL,
             zero_byte_violations INTEGER DEFAULT 0,
             recursion_flags INTEGER DEFAULT 0,
             status TEXT DEFAULT 'running',
             p50_latency REAL,
             p90_latency REAL,
             p99_latency REAL,
             retry_trace TEXT)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS session_latency_samples
            (session_id TEXT NOT NULL, latency REAL NOT NULL)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS session_retry_traces
            (session_id TEXT NOT NULL, trace TEXT NOT NULL)"""
    )


def _ensure_db_path(db_path: Path) -> None:
    """Ensure ``db_path`` exists and is a valid SQLite database.

    If the file is missing it is created. If it exists but is not a valid
    SQLite database, the corrupted file is moved aside and a fresh database is
    created in its place. This mirrors the behaviour of other parts of the
    project that automatically recover from database corruption.
    """

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        try:
            with db_path.open("rb") as fh:
                header = fh.read(16)
            if header[:16] != b"SQLite format 3\000":
                raise sqlite3.DatabaseError("invalid header")
        except sqlite3.DatabaseError:
            backup = db_path.with_suffix(db_path.suffix + ".corrupt")
            try:
                db_path.replace(backup)
            except OSError:
                db_path.unlink(missing_ok=True)
    # if db_path does not exist or was moved aside due to corruption, it will
    # be created automatically when a connection is opened later


def _retry(operation: Callable[[], None], retries: int = 3, delay: float = 0.1) -> None:
    """Run *operation* with simple retries on OperationalError."""
    for attempt in range(retries):
        try:
            operation()
            return
        except sqlite3.OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def start_session(session_id: str, *, workspace: Optional[str] = None) -> None:
    db_path = _db(workspace)
    _ensure_db_path(db_path)  # Ensure DB exists before operations

    def operation() -> None:
        with sqlite3.connect(db_path) as conn:
            _ensure(conn)
            conn.execute(
                """
                INSERT OR IGNORE INTO session_lifecycle (session_id, start_ts, status)
                VALUES(?, ?, 'running')
                """,
                (session_id, int(time.time())),
            )
            conn.commit()

    _retry(operation)


def record_latency(session_id: str, latency: float, *, workspace: Optional[str] = None) -> None:
    """Record a latency sample for ``session_id``."""
    db_path = _db(workspace)
    _ensure_db_path(db_path)

    def operation() -> None:
        with sqlite3.connect(db_path) as conn:
            _ensure(conn)
            conn.execute(
                "INSERT INTO session_latency_samples (session_id, latency) VALUES (?, ?)",
                (session_id, float(latency)),
            )
            conn.commit()

    _retry(operation)


def record_retry(session_id: str, trace: str, *, workspace: Optional[str] = None) -> None:
    """Record a retry trace for ``session_id``."""
    db_path = _db(workspace)
    _ensure_db_path(db_path)

    def operation() -> None:
        with sqlite3.connect(db_path) as conn:
            _ensure(conn)
            conn.execute(
                "INSERT INTO session_retry_traces (session_id, trace) VALUES (?, ?)",
                (session_id, trace),
            )
            conn.commit()

    _retry(operation)


def end_session(
    session_id: str,
    *,
    zero_byte_violations: int = 0,
    recursion_flags: int = 0,
    status: str = "success",
    workspace: Optional[str] = None,
) -> None:
    db_path = _db(workspace)
    _ensure_db_path(db_path)  # Ensure DB exists before operations

    def operation() -> None:
        with sqlite3.connect(db_path) as conn:
            _ensure(conn)
            cur = conn.execute("SELECT start_ts FROM session_lifecycle WHERE session_id=?", (session_id,))
            row = cur.fetchone()
            if row:
                start_ts = row[0]
            else:
                start_ts = int(time.time())
                conn.execute(
                    "INSERT OR IGNORE INTO session_lifecycle (session_id, start_ts, status) VALUES (?, ?, 'running')",
                    (session_id, start_ts),
                )
            end_ts = int(time.time())
            duration = time.time() - start_ts
            lat_cur = conn.execute(
                "SELECT latency FROM session_latency_samples WHERE session_id=?",
                (session_id,),
            )
            latencies = [r[0] for r in lat_cur.fetchall()]

            def percentile(values: list[float], pct: int) -> float | None:
                if not values:
                    return None
                values.sort()
                k = max(0, math.ceil(len(values) * (pct / 100)) - 1)
                return values[k]

            p50 = percentile(latencies, 50)
            p90 = percentile(latencies, 90)
            p99 = percentile(latencies, 99)

            retry_cur = conn.execute(
                "SELECT trace FROM session_retry_traces WHERE session_id=?",
                (session_id,),
            )
            retry_trace = ";".join(r[0] for r in retry_cur.fetchall())
            conn.execute(
                """UPDATE session_lifecycle SET end_ts=?, duration_seconds=?,
                zero_byte_violations=?, recursion_flags=?, status=?,
                p50_latency=?, p90_latency=?, p99_latency=?, retry_trace=? WHERE session_id=?""",
                (
                    end_ts,
                    float(duration),
                    int(zero_byte_violations),
                    int(recursion_flags),
                    status,
                    p50,
                    p90,
                    p99,
                    retry_trace,
                    session_id,
                ),
            )
            conn.commit()

    _retry(operation)
