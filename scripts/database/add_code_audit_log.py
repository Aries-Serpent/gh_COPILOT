#!/usr/bin/env python3
"""Add the ``code_audit_log`` table to analytics.db.

This utility creates the ``code_audit_log`` table if it does not
already exist and verifies database size compliance after the
operation. It follows the database-first pattern and can safely be
run multiple times.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from .size_compliance_checker import check_database_sizes

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS code_audit_log (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    placeholder_type TEXT NOT NULL,
    context TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_file_path
    ON code_audit_log(file_path);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_timestamp
    ON code_audit_log(timestamp);
"""


def add_table(db_path: Path) -> None:
    """Create ``code_audit_log`` table in ``db_path``."""
    start_time = datetime.now()
    logger.info("[START] add_table for %s", db_path)
    logger.info("Process ID: %s", os.getpid())

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(
        total=1, desc="create-table", unit="step"
    ) as bar:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        bar.update(1)
    logger.info("code_audit_log ensured in %s", db_path)
    check_database_sizes(db_path.parent)

    elapsed = datetime.now() - start_time
    logger.info("[SUCCESS] Completed in %s", str(elapsed))


def ensure_code_audit_log(db_path: Path) -> None:
    """Ensure ``code_audit_log`` table exists."""
    add_table(db_path)


__all__ = ["add_table", "ensure_code_audit_log"]


def ensure_code_audit_log(db_path: Path) -> None:
    """Ensure ``code_audit_log`` table exists with visual indicators."""
    start_time = datetime.now()
    logger.info("PROCESS STARTED: ensure_code_audit_log")
    logger.info("Start Time: %s", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Process ID: %d", os.getpid())
    with tqdm(total=1, desc="Ensuring table", unit="step") as bar:
        add_table(db_path)
        bar.update(1)
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("ensure_code_audit_log completed in %.2fs", duration)

    validator = SecondaryCopilotValidator(logger)
    if validator.validate_corrections([__file__]):
        logger.info("DUAL COPILOT VALIDATION: PASSED")
    else:
        logger.error("DUAL COPILOT VALIDATION: FAILED")


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

__all__ = ["add_table", "ensure_code_audit_log"]
