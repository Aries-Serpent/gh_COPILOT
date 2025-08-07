"""Codex session logging utilities."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from utils.cross_platform_paths import CrossPlatformPathManager


CODEX_LOG_DB = Path("databases/codex_log.db")
DB_NAME = "codex_log.db"
TABLE_NAME = "codex_log"


def init_db() -> None:
    """Initialize the Codex log database and create required tables."""
    CODEX_LOG_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CODEX_LOG_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_actions(
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                ts TEXT,
                action TEXT,
                statement TEXT,
                metadata TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_log (
                session_id TEXT,
                event TEXT,
                summary TEXT,
                ts TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def codex_log_cursor(db_name: str = DB_NAME) -> Iterator[sqlite3.Cursor]:
    """Yield a database cursor for batch Codex log inserts.

    Ensures the Codex log table exists and commits on success.
    """
    workspace: Path = CrossPlatformPathManager.get_workspace_path()
    db_path = workspace / "databases" / db_name
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_log (
                session_id TEXT,
                event TEXT,
                summary TEXT,
                ts TEXT
            )
            """
        )
        yield cursor
        conn.commit()
    finally:
        conn.close()


def log_codex_action(
    session_id: str, action: str, statement: str, metadata: str = ""
) -> None:
    """Log a Codex action to the database."""
    init_db()
    with sqlite3.connect(CODEX_LOG_DB) as conn:
        conn.execute(
            """
            INSERT INTO codex_actions (session_id, ts, action, statement, metadata)
            VALUES (?, datetime('now'), ?, ?, ?)
            """,
            (session_id, action, statement, metadata),
        )
        conn.commit()


def log_codex_start(session_id: str) -> None:
    """Record the start of a Codex session."""
    with codex_log_cursor() as cursor:
        cursor.execute(
            "INSERT INTO codex_log (session_id, event, summary, ts) VALUES (?, ?, ?, ?)",
            (session_id, "start", "", datetime.now(UTC).isoformat()),
        )


def log_codex_end(session_id: str, summary: str) -> None:
    """Record the end of a Codex session."""
    with codex_log_cursor() as cursor:
        cursor.execute(
            "INSERT INTO codex_log (session_id, event, summary, ts) VALUES (?, ?, ?, ?)",
            (session_id, "end", summary, datetime.now(UTC).isoformat()),
        )


__all__ = ["init_db", "codex_log_cursor", "log_codex_action", "log_codex_start", "log_codex_end"]
