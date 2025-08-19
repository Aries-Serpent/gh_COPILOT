
from __future__ import annotations

import json
import os
import sqlite3
import threading
from typing import Any, Dict, Optional

__all__ = ["log_event", "log_sync_operation", "get_db_path", "ensure_schema"]

_LOCK = threading.RLock()

def get_db_path(db_path: Optional[str]=None, test_mode: Optional[bool]=None) -> str:
    """
    Resolve effective DB path based on TEST_MODE and env overrides.
    TEST_MODE rules:
      - If ANALYTICS_DB_PATH is set, always use it (safe for tests).
      - Else, if TEST_MODE is truthy, use ':memory:' to avoid on-disk side effects.
      - Else, default to 'analytics.db'.
    """
    if db_path:
        return db_path
    env_db = os.getenv("ANALYTICS_DB_PATH")
    if env_db:
        return env_db
    if test_mode is None:
        test_mode = str(os.getenv("TEST_MODE","0")).strip().lower() in {"1","true","yes","on"}
    return ":memory:" if test_mode else "analytics.db"

def ensure_schema(conn: sqlite3.Connection) -> None:
    with conn:
        # Schema aligned with README (events table)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events(
          event_time TEXT DEFAULT (datetime('now')),
          level      TEXT,
          event      TEXT,
          details    TEXT
        );
        """)

def _connect(db_path: str) -> sqlite3.Connection:
    # If using URI (e.g., shared memory), enable uri param
    uri = db_path.startswith("file:")
    conn = sqlite3.connect(db_path, uri=uri, timeout=30, isolation_level=None, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def log_event(level: str, event: str, details: Dict[str, Any], *, db_path: Optional[str]=None, test_mode: Optional[bool]=None) -> None:
    """
    Insert a single row into events(level, event, details) with automatic event_time.
    details is JSON-encoded.
    """
    effective = get_db_path(db_path=db_path, test_mode=test_mode)
    payload = json.dumps(details, ensure_ascii=False, separators=(",",":"))
    with _LOCK:
        conn = _connect(effective)
        try:
            ensure_schema(conn)
            with conn:
                conn.execute(
                    "INSERT INTO events(level,event,details) VALUES(?,?,?)",
                    (level, event, payload),
                )
        finally:
            conn.close()

def log_sync_operation(file_path: str, count: int, status: str, *, db_path: Optional[str]=None, test_mode: Optional[bool]=None) -> None:
    """
    Structured convenience around log_event for sync operations on HARs or other artifacts.
    Writes event='sync_operation' with details JSON of file_path, count, status.
    """
    details = {"file_path": file_path, "count": int(count), "status": status}
    return log_event(level="INFO", event="sync_operation", details=details, db_path=db_path, test_mode=test_mode)
