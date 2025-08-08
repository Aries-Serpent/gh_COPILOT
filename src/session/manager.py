"""Minimal session manager used by tests.

The manager tracks resources that need validation when a session ends.
It is intentionally small and is **not** a drop-in replacement for the
production session manager.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3

from .validators import (
    check_logs,
    check_open_connections,
    check_temp_files,
    check_uncommitted_transactions,
    check_orphaned_sessions,
)


class SessionManager:
    """Coordinate shutdown validation for test sessions."""

    def __init__(
        self,
        log_dir: Path,
        temp_dir: Path | None = None,
        session_dir: Path | None = None,
    ) -> None:
        self.log_dir = Path(log_dir)
        self.temp_dir = Path(temp_dir) if temp_dir else self.log_dir.parent
        self.session_dir = Path(session_dir) if session_dir else self.log_dir.parent
        self._connections: list[sqlite3.Connection] = []

    def register_connection(self, conn: sqlite3.Connection) -> None:
        """Record a connection that should be closed on shutdown."""

        self._connections.append(conn)

    # --- shutdown -----------------------------------------------------
    def shutdown(self) -> None:
        """Run wrap-up validators.

        Each validator returns a list of offending items.  If any are
        present, a ``RuntimeError`` is raised to signal session wrap-up
        failure.
        """

        open_conns = check_open_connections(self._connections)
        if open_conns:
            raise RuntimeError("open connections detected")

        uncommitted = check_uncommitted_transactions(self._connections)
        if uncommitted:
            raise RuntimeError("uncommitted transactions detected")

        temp_files = check_temp_files(self.temp_dir)
        if temp_files:
            raise RuntimeError(f"temporary files remaining: {temp_files}")

        empty_logs = check_logs(self.log_dir)
        if empty_logs:
            raise RuntimeError(f"empty log files detected: {empty_logs}")

        orphaned = check_orphaned_sessions(self.session_dir)
        if orphaned:
            raise RuntimeError(f"orphaned sessions detected: {orphaned}")


__all__ = ["SessionManager"]
