#!/usr/bin/env python3
"""Ensure the ``violation_logs`` table exists in ``analytics.db``."""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from scripts.database.size_compliance_checker import check_database_sizes
from utils.log_utils import _log_event

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS violation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event TEXT,
    details TEXT NOT NULL,
    cause TEXT,
    remediation_path TEXT,
    rollback_trigger TEXT,
    count INTEGER
);
CREATE INDEX IF NOT EXISTS idx_violation_logs_timestamp
    ON violation_logs(timestamp);
"""


def add_table(db_path: Path, *, validate: bool = True) -> None:
    """Create ``violation_logs`` table in ``db_path``."""
    start_time = datetime.now()
    logger.info("[START] add_table for %s", db_path)
    logger.info("Process ID: %s", os.getpid())

    if validate:
        from enterprise_modules.compliance import validate_enterprise_operation

        if not validate_enterprise_operation(str(db_path.parent)):
            return
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(total=1, desc="create-table", unit="step") as bar:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        bar.update(1)
    logger.info("violation_logs ensured in %s", db_path)
    check_database_sizes(db_path.parent)
    _log_event({"event": "violation_logs_ready", "db": str(db_path)})
    from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator

    DualCopilotOrchestrator(logger).validator.validate_corrections([str(db_path)])

    elapsed = datetime.now() - start_time
    logger.info("[SUCCESS] Completed in %s", str(elapsed))


def ensure_violation_logs(db_path: Path, *, validate: bool = True) -> None:
    """Ensure ``violation_logs`` table exists."""
    add_table(db_path, validate=validate)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "analytics.db"
    start = datetime.now()
    add_table(db_path)
    etc = start + timedelta(seconds=1)
    logger.info(
        "Migration completed at %s | ETC was %s",
        datetime.utcnow().isoformat(),
        etc.strftime("%Y-%m-%d %H:%M:%S"),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

__all__ = ["add_table", "ensure_violation_logs"]
