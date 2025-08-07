from __future__ import annotations

from pathlib import Path
import sqlite3

CODEX_LOG_DB = Path("databases/codex_log.db")


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
        conn.commit()


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
