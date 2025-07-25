#!/usr/bin/env python3
"""Add the ``code_audit_log`` table to analytics.db.

This utility creates the ``code_audit_log`` table if it does not
already exist and verifies database size compliance after the
operation. It follows the database-first pattern and can safely be
run multiple times.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

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
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    logger.info("code_audit_log ensured in %s", db_path)
    check_database_sizes(db_path.parent)


def ensure_code_audit_log(db_path: Path) -> None:
    """Ensure ``code_audit_log`` table exists."""
    add_table(db_path)


__all__ = ["add_table", "ensure_code_audit_log"]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "analytics.db"
    add_table(db_path)
    logger.info("Migration completed at %s", datetime.utcnow().isoformat())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
