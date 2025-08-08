#!/usr/bin/env python3
"""Task stubs for the dedicated Codex log database workflow."""
"""Convenience wrappers for Codex action logging."""

from utils.codex_log_db import (
    finalize_codex_log_db,
    init_codex_log_db,
    log_codex_end,
    log_codex_start,
    record_codex_action,
)

def initialize_session(session_id: str) -> None:
    """Initialize logging for a Codex session.

    Parameters
    ----------
    session_id:
        Identifier for the active Codex session.
    """

    init_codex_log_db()
    log_codex_start(session_id)

def log_action(session_id: str, action: str, statement: str, metadata: str = "") -> None:
    """Record a Codex action and its statement.

    Parameters
    ----------
    session_id:
        Identifier for the current session.
    action:
        Short name describing the action.
    statement:
        Free-form text describing the action in detail.
    metadata:
        Optional JSON or text metadata to persist alongside the action.
    """

    record_codex_action(session_id, action, statement, metadata)

def finalize_session(session_id: str, summary: str) -> None:
    """Finalize the Codex session log and stage it for commit.

    Parameters
    ----------
    session_id:
        Identifier for the active session.
    summary:
        Human-readable summary of the session outcome.
    """

    log_codex_end(session_id, summary)
    finalize_codex_log_db()

__all__ = [
    "initialize_session",
    "log_action",
    "finalize_session",
]
