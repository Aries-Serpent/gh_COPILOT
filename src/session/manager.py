"""Minimal session manager used by tests.

The manager tracks resources that need validation when a session ends.
It is intentionally small and is **not** a drop-in replacement for the
production session manager.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3

from .validators import validate_lifecycle


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

        issues = validate_lifecycle(
            self._connections,
            log_dir=self.log_dir,
            temp_dir=self.temp_dir,
            session_dir=self.session_dir,
        )
        if issues:
            joined = "; ".join(f"{k} detected: {v}" for k, v in issues.items())
            raise RuntimeError(joined)


__all__ = ["SessionManager"]
