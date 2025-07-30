#!/usr/bin/env python3
"""Log error notifier.

This module scans log files for error messages and records notifications in
``analytics.db``. It demonstrates the DUAL COPILOT pattern by monitoring log
content, logging each error via :func:`utils.log_utils._log_event`, and
issuing a summary notification when errors are detected.

Functions are intentionally small to keep logic testable. ``monitor_logs``
returns the number of error lines found across the supplied log files. The
``notify`` helper records a single notification event summarizing the total
errors discovered.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional

from utils.log_utils import _log_event

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

__all__ = ["monitor_logs", "notify"]


def monitor_logs(log_files: Iterable[Path], db_path: Optional[Path] = None) -> int:
    """Scan ``log_files`` for lines containing ``"ERROR"`` and log each one.

    Parameters
    ----------
    log_files:
        Iterable of paths to log files to inspect.
    db_path:
        Optional path to the analytics database. Defaults to ``analytics.db`` in
        the workspace.

    Returns
    -------
    int
        Total number of error lines found.
    """

    path = db_path or DB_PATH
    error_count = 0

    for log_file in log_files:
        try:
            with open(log_file, "r", encoding="utf-8") as fh:
                for line in fh:
                    if "ERROR" in line.upper():
                        _log_event(
                            {"file": str(log_file), "error": line.strip()},
                            table="log_errors",
                            db_path=path,
                            test_mode=False,
                        )
                        error_count += 1
        except FileNotFoundError:
            continue

    if error_count:
        notify(error_count, db_path=path)

    return error_count


def notify(error_count: int, db_path: Optional[Path] = None) -> None:
    """Record a notification event for ``error_count`` errors."""

    path = db_path or DB_PATH
    _log_event(
        {"errors_found": error_count},
        table="log_notifications",
        db_path=path,
        test_mode=False,
    )


if __name__ == "__main__":  # pragma: no cover - manual invocation
    import sys

    count = monitor_logs([Path(p) for p in sys.argv[1:]])
    print(f"Found {count} error lines")
