"""Session-aware Codex action logging utilities."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

_CODEX_LOG_DB: Optional[Path] = None
_SESSION_ID: Optional[str] = None


def init_codex_log_db(session_id: str) -> Path:
    """Initialize the Codex log database for the given ``session_id``.

    The database contains a ``codex_logs`` table used to record actions
    taken by Codex during the session. The table is created if it does
    not already exist.
    """

    global _CODEX_LOG_DB, _SESSION_ID

    _SESSION_ID = session_id
    if _CODEX_LOG_DB is None:
        _CODEX_LOG_DB = Path("databases/codex_logs.db")

    _CODEX_LOG_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_CODEX_LOG_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_logs(
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                timestamp TEXT,
                action TEXT,
                statement TEXT,
                metadata TEXT
            )
            """
        )
        conn.commit()

    return _CODEX_LOG_DB


def record_codex_action(
    action: str, statement: str, *, metadata: dict | None = None
) -> None:
    """Insert a Codex action entry into the log database."""

    if _CODEX_LOG_DB is None or _SESSION_ID is None:
        raise RuntimeError("Codex log database has not been initialized")

    with sqlite3.connect(_CODEX_LOG_DB) as conn:
        conn.execute(
            """
            INSERT INTO codex_logs (
                session_id, timestamp, action, statement, metadata
            ) VALUES (?, datetime('now'), ?, ?, ?)
            """,
            (
                _SESSION_ID,
                action,
                statement,
                json.dumps(metadata) if metadata is not None else "",
            ),
        )
        conn.commit()


def finalize_codex_log_db() -> Path:
    """Finalize logging and return the database file path."""

    if _CODEX_LOG_DB is None:
        raise RuntimeError("Codex log database has not been initialized")

    return _CODEX_LOG_DB


__all__ = [
    "init_codex_log_db",
    "record_codex_action",
    "finalize_codex_log_db",
]

