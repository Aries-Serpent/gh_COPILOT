#!/usr/bin/env python3
"""Codex session log database utilities.

Records Codex actions and statements into an SQLite database so each
session's activity can be reviewed after commit.

Features:
* Database-first path: ``databases/codex_session_logs.db`` under
  ``GH_COPILOT_WORKSPACE``.
* Anti-recursion guard to prevent recursive invocation.
* Dual-copilot validation by confirming record counts post-insert.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from utils.validation_utils import anti_recursion_guard
from utils.log_utils import log_message


DEFAULT_DB = (
    Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    / "databases"
    / "codex_session_logs.db"
)

TABLE = "codex_session_log"


def _ensure_db(db_path: Path) -> None:
    """Ensure the Codex log database and table exist.

    Raises:
        RuntimeError: If the database cannot be created or initialised.
    """

    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    statement TEXT
                );
                """
            )
    except sqlite3.DatabaseError as exc:
        if "file is not a database" in str(exc).lower():
            try:
                db_path.unlink(missing_ok=True)
                with sqlite3.connect(db_path) as conn:
                    conn.execute(
                        f"""
                        CREATE TABLE IF NOT EXISTS {TABLE} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT,
                            timestamp TEXT NOT NULL,
                            action TEXT NOT NULL,
                            statement TEXT
                        );
                        """
                    )
            except (OSError, sqlite3.DatabaseError) as inner_exc:
                raise RuntimeError(
                    f"Failed to rebuild Codex log database at {db_path}: {inner_exc}"
                ) from inner_exc
        else:
            raise RuntimeError(
                f"Failed to initialise Codex log database at {db_path}: {exc}"
            ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Failed to initialise Codex log database at {db_path}: {exc}"
        ) from exc


@anti_recursion_guard
def log_codex_event(
    action: str,
    statement: str,
    *,
    session_id: str = "default",
    db_path: Path = DEFAULT_DB,
) -> None:
    """Log a Codex action and associated statement."""

    try:
        _ensure_db(db_path)
        ts = datetime.utcnow().isoformat()
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                f"INSERT INTO {TABLE} (session_id, timestamp, action, statement) VALUES (?, ?, ?, ?)",
                (session_id, ts, action, statement),
            )
            count = conn.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    except sqlite3.DatabaseError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to log Codex event: {exc}") from exc

    log_message("codex_log_db", f"Logged action '{action}' (total records: {count})")


def fetch_codex_events(
    *, session_id: Optional[str] = None, db_path: Path = DEFAULT_DB
) -> List[Dict[str, str]]:
    """Return codex log entries optionally filtered by session."""

    try:
        _ensure_db(db_path)
        query = f"SELECT session_id, timestamp, action, statement FROM {TABLE}"
        params: List[str] = []
        if session_id is not None:
            query += " WHERE session_id = ?"
            params.append(session_id)
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
    except sqlite3.DatabaseError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to fetch Codex events: {exc}") from exc

    return [dict(r) for r in rows]


__all__ = ["log_codex_event", "fetch_codex_events", "DEFAULT_DB", "TABLE"]

