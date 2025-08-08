#!/usr/bin/env python3
"""Task stubs for the dedicated Codex log database workflow."""
from utils.codex_log_db import (
    finalize_codex_log_db,
    init_codex_log_db,
    log_codex_end,
    log_codex_start,
    record_codex_action,
)

def initialize_session(session_id: str) -> None:
    """Initialize logging for a Codex session.

    This sets up the log database and records the start event for the
    provided ``session_id``.
    """
    init_codex_log_db()
    log_codex_start(session_id)

def log_action(
    session_id: str,
    action: str,
    statement: str,
    metadata: str = "",
) -> None:
    """Record a Codex action and its statement.

    The action details are written to ``codex_log.db`` for later review.
    """
    record_codex_action(session_id, action, statement, metadata)

def finalize_session(session_id: str, summary: str) -> None:
    """Finalize the Codex session log and stage it for commit.

    Records the end event and copies the log database to the session log
    archive, staging both databases with ``git add``.
    """
    log_codex_end(session_id, summary)
    finalize_codex_log_db()

__all__ = [
    "initialize_session",
    "log_action",
    "finalize_session",
]
