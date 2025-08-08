"""Utility for logging Codex actions and statements.

This module provides a lightweight interface for recording Codex
operations during a session.  Each entry is stored in a SQLite database
(`databases/codex_logs.db`) with columns capturing the UTC timestamp,
action name, and the associated statement.  The database is staged for
commit (via Git LFS) when finalised.
"""

from __future__ import annotations

from datetime import UTC, datetime
import sqlite3
import subprocess
from pathlib import Path
from typing import Optional

from utils.cross_platform_paths import CrossPlatformPathManager

DB_PATH = Path("databases/codex_logs.db")


def _workspace_path() -> Path:
    return CrossPlatformPathManager.get_workspace_path()


def init_db() -> Path:
    """Ensure the logging database and table exist."""
    workspace = _workspace_path()
    db_file = workspace / DB_PATH
    db_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS codex_logs(
                id INTEGER PRIMARY KEY,
                ts TEXT NOT NULL,
                action TEXT NOT NULL,
                statement TEXT NOT NULL
            )
            """
        )
        conn.commit()
    return db_file


def log_action(action: str, statement: str, *, ts: Optional[str] = None) -> None:
    """Insert a Codex log entry with a UTC timestamp."""
    db_file = init_db()
    ts_val = ts or datetime.now(UTC).isoformat()
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            "INSERT INTO codex_logs (ts, action, statement) VALUES (?, ?, ?)",
            (ts_val, action, statement),
        )
        conn.commit()


def finalize_db() -> Path:
    """Stage the database for commit and return its path."""
    workspace = _workspace_path()
    db_file = workspace / DB_PATH
    if db_file.exists():
        subprocess.run(
            ["git", "add", str(DB_PATH)],
            cwd=workspace,
            check=True,
        )
    return db_file

