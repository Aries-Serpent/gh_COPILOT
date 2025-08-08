"""Codex action logging utilities."""

from __future__ import annotations

import sqlite3
import shutil
from pathlib import Path


CODEX_LOG_DB = Path("databases/codex_log.db")
CODEX_SESSION_LOG_DB = Path("databases/codex_session_logs.db")


def init_db() -> None:
    """Create the ``codex_actions`` table if it doesn't exist."""
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
        conn.commit()


def log_codex_action(
    session_id: str, action: str, statement: str, metadata: str = "",
) -> None:
    """Insert a Codex action entry into the database."""
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


def finalize_codex_log_db(destination: Path | None = None) -> Path:
    """Close the Codex log database and copy it to ``destination``.

    Parameters
    ----------
    destination:
        Optional path for the copied database. Defaults to
        ``databases/codex_session_logs.db``.

    Returns
    -------
    Path
        The path to the copied database.
    """
    init_db()
    dest = destination or CODEX_SESSION_LOG_DB
    dest.parent.mkdir(parents=True, exist_ok=True)
    if CODEX_LOG_DB.exists():
        shutil.copy2(CODEX_LOG_DB, dest)
    return dest


__all__ = [
    "CODEX_LOG_DB",
    "CODEX_SESSION_LOG_DB",
    "init_db",
    "log_codex_action",
    "finalize_codex_log_db",
]

