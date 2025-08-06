#!/usr/bin/env python3
"""Remove obsolete records from :mod:`production.db`.

This utility follows the Dual Copilot pattern with basic visual
processing indicators. It deletes all rows from ``obsolete_table`` and
verifies the cleanup in a secondary validation phase.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Tuple

from tqdm import tqdm
from secondary_copilot_validator import SecondaryCopilotValidator

DB_PATH = Path("databases/production.db")
TABLE = "obsolete_table"


def _primary_cleanup(conn: sqlite3.Connection) -> int:
    """Delete all rows from :data:`TABLE`.

    Returns the number of rows removed. If the table does not exist, no
    rows are removed and zero is returned.
    """

    if not _table_exists(conn, TABLE):
        logging.info("Table %s not present; nothing to clean", TABLE)
        return 0

    cur = conn.execute(f"DELETE FROM {TABLE}")
    return cur.rowcount


def _secondary_validation(conn: sqlite3.Connection) -> bool:
    """Verify :data:`TABLE` has no remaining rows."""

    if not _table_exists(conn, TABLE):
        return True
    remaining = conn.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    return remaining == 0


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        ).fetchone()
        is not None
    )


def cleanup_obsolete_entries(db_path: Path = DB_PATH) -> Tuple[int, bool]:
    """Clean ``obsolete_table`` from ``db_path``.

    Returns a tuple of ``(rows_deleted, validation_passed)``.
    """

    start = datetime.now()
    logging.info("Start: %s", start.strftime("%Y-%m-%d %H:%M:%S"))
    logging.info("PID: %s", os.getpid())

    with sqlite3.connect(db_path) as conn:
        with tqdm(total=1, desc="Cleaning", unit="step") as bar:
            deleted = _primary_cleanup(conn)
            bar.update(1)

    with sqlite3.connect(db_path) as conn:
        valid = _secondary_validation(conn)

    SecondaryCopilotValidator().validate_corrections([str(db_path)])

    logging.info("Rows deleted: %s", deleted)
    logging.info("Validation: %s", "passed" if valid else "failed")
    logging.info("Completed in %s", datetime.now() - start)
    return deleted, valid


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cleanup_obsolete_entries()
