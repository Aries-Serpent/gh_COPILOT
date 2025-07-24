#!/usr/bin/env python3
"""Create the ``code_audit_log`` table in ``analytics.db``.

This utility ensures the analytics database contains the table used by
placeholder audit scripts. It can be run independently or imported by
other modules to guarantee the table exists before inserts occur.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from utils.logging_utils import setup_enterprise_logging

from .size_compliance_checker import check_database_sizes

DEFAULT_ANALYTICS_DB = Path("databases") / "analytics.db"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS code_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    placeholder_type TEXT NOT NULL,
    context TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_file ON code_audit_log(file_path);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_time ON code_audit_log(timestamp);
"""


def ensure_code_audit_log(db_path: Path = DEFAULT_ANALYTICS_DB) -> None:
    """Create ``code_audit_log`` table in ``db_path`` if missing."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(CREATE_SQL)


def main(db_path: Path = DEFAULT_ANALYTICS_DB) -> None:
    """Entry point for standalone execution."""
    logger = setup_enterprise_logging()
    ensure_code_audit_log(db_path)
    sizes = check_database_sizes(db_path.parent)
    logger.info(
        "code_audit_log ensured. %s size: %.2f MB",
        db_path.name,
        sizes.get(db_path.name, 0.0),
    )


if __name__ == "__main__":
    main()

