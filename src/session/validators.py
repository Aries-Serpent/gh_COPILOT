"""Simple validators used during session shutdown.

The functions in this module intentionally avoid external dependencies
and keep the checks very small.  They return the list of offending items
so callers can decide how to handle validation failures.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3


def check_open_connections(connections: list[sqlite3.Connection]) -> list[sqlite3.Connection]:
    """Return connections that are still usable.

    ``sqlite3`` connections expose ``execute`` even when a transaction is
    active; attempting to issue a trivial query is a straightforward way
    to determine whether the connection has already been closed.  Any
    connection that executes the probe successfully is considered open
    and returned in the result list.
    """

    open_conns: list[sqlite3.Connection] = []
    for conn in connections:
        try:
            conn.execute("SELECT 1")
        except Exception:
            continue
        else:
            open_conns.append(conn)
    return open_conns


def check_temp_files(temp_dir: Path) -> list[Path]:
    """Return ``*.tmp`` files located in ``temp_dir``."""

    directory = Path(temp_dir)
    return [p for p in directory.glob("*.tmp") if p.is_file()]


def check_logs(log_dir: Path) -> list[Path]:
    """Return empty ``*.log`` files present in ``log_dir``."""

    directory = Path(log_dir)
    offending: list[Path] = []
    for log in directory.glob("*.log"):
        if log.is_file() and log.stat().st_size == 0:
            offending.append(log)
    return offending


def check_uncommitted_transactions(
    connections: list[sqlite3.Connection],
) -> list[sqlite3.Connection]:
    """Return connections that have pending transactions."""

    return [conn for conn in connections if conn.in_transaction]


def check_orphaned_sessions(session_dir: Path) -> list[Path]:
    """Return ``session-*.json`` files located in ``session_dir``."""

    directory = Path(session_dir)
    return [p for p in directory.glob("session-*.json") if p.is_file()]


def validate_lifecycle(
    connections: list[sqlite3.Connection],
    *,
    log_dir: Path,
    temp_dir: Path,
    session_dir: Path,
) -> dict[str, list]:
    """Run all validators and return a mapping of failures.

    Each key in the returned dictionary corresponds to a specific
    validator.  The value is the list of offending items produced by the
    underlying check.  An empty dictionary indicates that the session has
    completed cleanly.
    """

    issues: dict[str, list] = {}

    open_conns = check_open_connections(connections)
    if open_conns:
        issues["open_connections"] = open_conns

    uncommitted = check_uncommitted_transactions(connections)
    if uncommitted:
        issues["uncommitted_transactions"] = uncommitted

    temp_files = check_temp_files(temp_dir)
    if temp_files:
        issues["temp_files"] = temp_files

    empty_logs = check_logs(log_dir)
    if empty_logs:
        issues["empty_logs"] = empty_logs

    orphaned = check_orphaned_sessions(session_dir)
    if orphaned:
        issues["orphaned_sessions"] = orphaned

    return issues


__all__ = [
    "check_open_connections",
    "check_temp_files",
    "check_logs",
    "check_uncommitted_transactions",
    "check_orphaned_sessions",
    "validate_lifecycle",
]
