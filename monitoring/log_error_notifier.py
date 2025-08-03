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
import threading
from pathlib import Path
from time import sleep
from typing import Iterable, Optional

from utils.log_utils import _log_event

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

LOG_ERROR_ALERT_THRESHOLD = 10

__all__ = ["monitor_logs", "notify", "schedule_log_monitoring", "LOG_ERROR_ALERT_THRESHOLD"]


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
    severity = "ALERT" if error_count > LOG_ERROR_ALERT_THRESHOLD else "INFO"
    _log_event(
        {"errors_found": error_count, "severity": severity},
        table="log_notifications",
        db_path=path,
        test_mode=False,
    )


def schedule_log_monitoring(
    log_files: Iterable[Path],
    interval: float,
    db_path: Optional[Path] = None,
    stop_event: Optional[threading.Event] = None,
) -> threading.Thread:
    """Periodically scan ``log_files`` and push metrics to ``analytics.db``.

    A background thread runs :func:`monitor_logs` every ``interval`` seconds
    until ``stop_event`` is set.

    Parameters
    ----------
    log_files:
        Files to monitor for error lines.
    interval:
        Number of seconds between scans.
    db_path:
        Optional path to the analytics database. Defaults to
        ``analytics.db`` in the workspace.
    stop_event:
        Optional :class:`threading.Event` used to signal the thread to stop.

    Returns
    -------
    threading.Thread
        The started daemon thread.
    """

    def _loop() -> None:
        while stop_event is None or not stop_event.is_set():
            monitor_logs(log_files, db_path=db_path)
            if stop_event is None:
                sleep(interval)
            else:
                stop_event.wait(interval)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":  # pragma: no cover - manual invocation
    import sys

    count = monitor_logs([Path(p) for p in sys.argv[1:]])
    print(f"Found {count} error lines")
