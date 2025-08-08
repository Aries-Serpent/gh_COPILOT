"""Codex action logging utilities."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
import shutil
import subprocess
from pathlib import Path
from typing import Iterator

from utils.cross_platform_paths import CrossPlatformPathManager


CODEX_LOG_DB = Path("databases/codex_log.db")
CODEX_SESSION_LOG_DB = Path("databases/codex_session_logs.db")
DB_NAME = "codex_log.db"


def init_db() -> None:
    """Create required Codex logging tables if they don't exist."""
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
            CREATE TABLE IF NOT EXISTS codex_log(
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
    """Return a cursor for batch ``codex_log`` inserts."""
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


@contextmanager
def codex_actions_cursor(db_path: Path | None = None) -> Iterator[sqlite3.Cursor]:
    """Return a cursor for batch ``codex_actions`` inserts."""
    if db_path is None:
        workspace = CrossPlatformPathManager.get_workspace_path()
        db_path = workspace / "databases" / DB_NAME
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
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
        yield cursor
        conn.commit()
    finally:
        conn.close()


def log_codex_action(
    session_id: str,
    action: str,
    statement: str,
    metadata: str | dict | list | None = "",
) -> None:
    """Log a single Codex action with UTC timestamp.

    ``metadata`` may be a string or JSON-serialisable object.
    """
    if isinstance(metadata, (dict, list)):
        metadata_str = json.dumps(metadata)
    else:
        metadata_str = metadata or ""
    ts = datetime.now(UTC).isoformat()
    with codex_actions_cursor(CODEX_LOG_DB) as cursor:
        cursor.execute(
            """
            INSERT INTO codex_actions (session_id, ts, action, statement, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, ts, action, statement, metadata_str),
        )


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


def finalize_codex_log_db() -> Path:
    """Copy the log database to ``codex_session_logs.db`` and stage for commit.

    Returns the path to ``codex_session_logs.db`` for convenience.
    """
    workspace = CrossPlatformPathManager.get_workspace_path()
    src = workspace / CODEX_LOG_DB
    dst = workspace / CODEX_SESSION_LOG_DB
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        subprocess.run(
            [
                "git",
                "add",
                str(src.relative_to(workspace)),
                str(dst.relative_to(workspace)),
            ],
            cwd=workspace,
            check=True,
        )
    return dst


def init_codex_log_db() -> None:
    """Alias for :func:`init_db` to initialize the Codex log database."""
    init_db()


def record_codex_action(
    session_id: str,
    action: str,
    statement: str,
    metadata: str | dict | list | None = "",
) -> None:
    """Alias for :func:`log_codex_action` for clarity."""
    log_codex_action(session_id, action, statement, metadata)


class CodexSessionLogger:
    """Context manager for dedicated Codex session logging.

    This helper initializes the log database, records session start and end
    events, and stages the databases for commit once the session completes.
    """

    def __init__(self, session_id: str, *, summary: str = "session complete") -> None:
        self.session_id = session_id
        self.summary = summary

    def __enter__(self) -> "CodexSessionLogger":
        init_codex_log_db()
        log_codex_start(self.session_id)
        return self

    def log(self, action: str, statement: str, metadata: str = "") -> None:
        """Record a Codex action and statement for this session."""
        record_codex_action(self.session_id, action, statement, metadata)

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        if exc is not None:
            end_summary = f"error: {exc}"
        else:
            end_summary = self.summary
        log_codex_end(self.session_id, end_summary)
        finalize_codex_log_db()


__all__ = [
    "CODEX_LOG_DB",
    "CODEX_SESSION_LOG_DB",
    "init_db",
    "codex_log_cursor",
    "codex_actions_cursor",
    "log_codex_action",
    "log_codex_start",
    "log_codex_end",
    "init_codex_log_db",
    "record_codex_action",
    "finalize_codex_log_db",
    "CodexSessionLogger",
]