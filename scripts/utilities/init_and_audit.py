"""Initialize databases and run code placeholder audit.

This utility sets up required SQLite databases if they do not
exist and then invokes :mod:`scripts.code_placeholder_audit`.
It logs operations for compliance tracking.
"""
from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import List

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import code_placeholder_audit

LOGGER = logging.getLogger(__name__)



def ensure_database(db_path: Path, ddl: List[str]) -> None:
    """Create ``db_path`` with the provided DDL statements if missing."""
    if db_path.exists():
        return
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        for stmt in ddl:
            conn.execute(stmt)
    LOGGER.info("Created database %s", db_path)


def run() -> None:
    """Run initialization and audit."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
    production_db = workspace / "databases" / "production.db"
    analytics_db = workspace / "databases" / "analytics.db"

    ensure_database(
        production_db,
        [
            "CREATE TABLE IF NOT EXISTS template_placeholders (placeholder_name TEXT)",
        ],
    )
    ensure_database(
        analytics_db,
        [
            "CREATE TABLE IF NOT EXISTS code_audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, line_number INTEGER, context TEXT, timestamp TEXT)"
        ],
    )

    code_placeholder_audit.main(simulate=True)


if __name__ == "__main__":  # pragma: no cover
    run()
