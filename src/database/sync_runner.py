"""Run database synchronization with logging.

This module provides a convenience wrapper around :class:`Engine` that logs
the lifecycle of a synchronization run. Logs are written to ``logs/sync`` with
rotation and retention.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, Dict, Optional

from .engine import Engine


LOG_DIR = Path("logs/sync")
LOG_FILE = LOG_DIR / "sync.log"

logger = logging.getLogger(__name__)


def _configure_logger() -> None:
    """Configure the rotating file logger if not already configured."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if logger.handlers:
        return

    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


_configure_logger()


def run_sync(
    a_path: str | Path,
    b_path: str | Path,
    log_hook: Optional[Callable[[str, Dict[str, str]], None]] = None,
) -> None:
    """Synchronize two SQLite databases and log start, success, and errors."""

    ctx = {"a_path": str(a_path), "b_path": str(b_path)}
    logger.info("Sync started %s", ctx)
    if log_hook:
        log_hook("sync.start", ctx)
    try:
        engine_a = Engine(a_path)
        engine_b = Engine(b_path)
        engine_a.sync_with(engine_b)
        logger.info("Sync completed successfully %s", ctx)
        if log_hook:
            log_hook("sync.end", ctx)
    except Exception as exc:  # pragma: no cover - ensures logging of unexpected errors
        logger.exception("Sync failed %s", ctx)
        if log_hook:
            log_hook("sync.error", {**ctx, "exception": repr(exc)})
        raise

