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


__all__ = ["check_open_connections", "check_temp_files", "check_logs"]

