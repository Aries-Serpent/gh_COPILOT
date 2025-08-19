#!/usr/bin/env python3
"""Ensure the ``code_audit_log`` table exists in ``analytics.db``.

This module follows the database-first pattern. It creates the table if
missing and verifies size compliance after the operation. The migration
is idempotent and safe to run multiple times.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from scripts.database.size_compliance_checker import check_database_sizes

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
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(total=1, desc="create-table", unit="step") as bar:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        bar.update(1)
    logger.info("code_audit_log ensured in %s", db_path)
    check_database_sizes(db_path.parent)

    elapsed = datetime.now() - start_time
    logger.info("[SUCCESS] Completed in %s", str(elapsed))


def ensure_code_audit_log(db_path: Path) -> None:
    """Ensure ``code_audit_log`` table exists (wrapper for :func:`add_table`)."""
    add_table(db_path)


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
