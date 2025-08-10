"""CLI wrapper for :mod:`validation.protocols.session`."""

import sqlite3
import sys
import traceback
from datetime import datetime

from validation.protocols.session import SessionProtocolValidator
from utils.cross_platform_paths import verify_environment_variables
from utils.validation_utils import anti_recursion_guard
from utils.logging_utils import ANALYTICS_DB

__all__ = ["SessionProtocolValidator", "main"]


def _log_session_event(message: str) -> None:
    """Persist a session log entry to ``analytics.db``."""
    ts = datetime.utcnow().isoformat()
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS session_logs (
                ts TEXT NOT NULL,
                message TEXT NOT NULL
            )"""
        )
        conn.execute(
            "INSERT INTO session_logs (ts, message) VALUES (?, ?)",
            (ts, message),
        )


def _check_recursion_depth(limit: int | None = None) -> None:
    """Log an anomaly if call stack depth exceeds ``limit``."""
    depth = len(traceback.extract_stack())
    max_depth = limit or sys.getrecursionlimit()
    if depth > max_depth:
        _log_session_event(f"recursion_depth_exceeded:{depth}/{max_depth}")


@anti_recursion_guard
def main() -> int:
    """Delegate to :class:`~validation.protocols.session.SessionProtocolValidator`."""
    _check_recursion_depth()
    verify_environment_variables()
    return SessionProtocolValidator.main()


if __name__ == "__main__":
    raise SystemExit(main())
