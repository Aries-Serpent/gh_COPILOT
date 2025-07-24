#!/usr/bin/env python3
"""Utility to add `code_audit_log` table to analytics.db."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from utils.logging_utils import setup_enterprise_logging

from .size_compliance_checker import check_database_sizes

logger = logging.getLogger(__name__)

SQL = """
CREATE TABLE IF NOT EXISTS code_audit_log (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    placeholder_type TEXT,
    context TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_file_path ON code_audit_log(file_path);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_timestamp ON code_audit_log(timestamp);
"""


def create_table(db_path: Path) -> None:
    """Create the code_audit_log table if missing."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        for stmt in filter(None, SQL.split(";")):
            conn.execute(stmt)
        conn.commit()


def main(db_path: Path | None = None) -> None:
    analytics = db_path or Path.cwd() / "databases" / "analytics.db"
    logger.info("Adding code_audit_log to %s", analytics)
    start = datetime.now()
    with tqdm(total=1, desc="Creating table", unit="task") as bar:
        create_table(analytics)
        bar.update(1)
    duration = (datetime.now() - start).total_seconds()
    logger.info("Table creation completed in %.2fs", duration)
    check_database_sizes(analytics.parent)


if __name__ == "__main__":
    setup_enterprise_logging()
    main()

