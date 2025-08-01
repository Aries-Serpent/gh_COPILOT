"""Ensure `enhanced_lessons_learned` exists in production database.

This script checks the ``production.db`` for the
``enhanced_lessons_learned`` table and creates it using the schema
from ``learning_monitor.db`` when missing.  Default values are preserved
to match the reference schema.

The operation follows the database-first pattern: ``production.db`` is
inspected before any schema is copied from the reference database.

Running the script is idempotent and safe to execute multiple times.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

PRODUCTION_DB = Path("databases/production.db")
REFERENCE_DB = Path("databases/learning_monitor.db")
TABLE_NAME = "enhanced_lessons_learned"


def ensure_enhanced_lessons_learned_table(
    production_db: Path = PRODUCTION_DB, reference_db: Path = REFERENCE_DB
) -> bool:
    """Ensure the lessons learned table exists in ``production_db``.

    Parameters
    ----------
    production_db:
        Path to the production SQLite database.
    reference_db:
        Path to the database containing the reference schema.

    Returns
    -------
    bool
        ``True`` if the table existed or was created successfully.
    """

    if not production_db.exists():
        raise FileNotFoundError(f"{production_db} not found")

    with sqlite3.connect(production_db) as prod_conn:
        cur = prod_conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (TABLE_NAME,),
        )
        if cur.fetchone():
            return True

        # Fetch creation SQL from the reference database
        with sqlite3.connect(reference_db) as ref_conn:
            ref_cur = ref_conn.cursor()
            ref_cur.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                (TABLE_NAME,),
            )
            row = ref_cur.fetchone()
            if row is None:
                raise RuntimeError(
                    f"Reference table {TABLE_NAME} not found in {reference_db}"
                )
            create_sql = row[0]

        prod_conn.executescript(create_sql)
        prod_conn.commit()

        # Dual-copilot validation: re-check table existence
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (TABLE_NAME,),
        )
        return cur.fetchone() is not None


if __name__ == "__main__":
    if ensure_enhanced_lessons_learned_table():
        print(f"{TABLE_NAME} table ensured in {PRODUCTION_DB}")

