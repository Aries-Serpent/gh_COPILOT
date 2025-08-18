"""Thread-safe session logging backed by SQLite."""

from __future__ import annotations

import contextlib
import datetime as dt
import os
import pathlib
import sqlite3
import threading
import uuid


_DB_ENV = "CODEX_SESSION_DB"
_DEFAULT_DB = "codex_session_log.db"


class _ConnLocal(threading.local):
    """Per-thread connection holder."""

    def __init__(self) -> None:  # pragma: no cover - trivial
        super().__init__()
        self.conn: sqlite3.Connection | None = None


class SessionLogger:
    """Lightweight session logger with WAL and per-thread connections."""

    def __init__(self, db_path: str | None = None, session_id: str | None = None) -> None:
        root = pathlib.Path.cwd()
        db_override = os.getenv(_DB_ENV)
        self.db_path = db_path or db_override or str((root / _DEFAULT_DB).resolve())
        self._local = _ConnLocal()
        self._write_lock = threading.Lock()
        self.session_id = session_id or os.getenv("CODEX_SESSION_ID") or str(uuid.uuid4())
        self._init_db()

    # ------------------------------------------------------------------
    # Internal helpers
    def _get_conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout=5000;")
            self._local.conn = conn
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_events(
                    session_id TEXT,
                    timestamp  TEXT,
                    role       TEXT,
                    message    TEXT,
                    PRIMARY KEY(session_id, timestamp)
                );
                """
            )
            conn.commit()

    def _log(self, role: str, message: str) -> None:
        ts = dt.datetime.utcnow().isoformat(timespec="microseconds") + "Z"
        with self._write_lock:
            conn = self._get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO session_events(session_id, timestamp, role, message) VALUES(?,?,?,?)",
                (self.session_id, ts, role, message),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Public API
    def log_session_start(self, note: str = "session.start") -> None:
        self._log("system", note)

    def log_session_end(self, note: str = "session.end") -> None:
        self._log("system", note)

    def log_message(self, role: str, message: str) -> None:
        self._log(role, message)

    @contextlib.contextmanager
    def session_context(
        self, start_note: str = "session.start", end_note: str = "session.end"
    ):
        self.log_session_start(start_note)
        try:
            yield self
        finally:
            self.log_session_end(end_note)

