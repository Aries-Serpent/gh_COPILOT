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
DEFAULT_COLUMNS = [
    "description",
    "source",
    "timestamp",
    "validation_status",
    "tags",
]


def _get_column_defaults(conn: sqlite3.Connection) -> dict[str, str | None]:
    """Return mapping of column name to default value for ``TABLE_NAME``."""
    info = conn.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()
    return {row[1]: row[4] for row in info}


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
        if not cur.fetchone():
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
        if cur.fetchone() is None:
            return False

    with sqlite3.connect(production_db) as prod_conn, sqlite3.connect(
        reference_db
    ) as ref_conn:
        prod_defaults = _get_column_defaults(prod_conn)
        ref_defaults = _get_column_defaults(ref_conn)

    for column in DEFAULT_COLUMNS:
        if prod_defaults.get(column) != ref_defaults.get(column):
            raise RuntimeError(
                f"Default mismatch for column {column}: {prod_defaults.get(column)} != {ref_defaults.get(column)}"
            )

    return True


if __name__ == "__main__":
    if ensure_enhanced_lessons_learned_table():
        print(f"{TABLE_NAME} table ensured in {PRODUCTION_DB}")

