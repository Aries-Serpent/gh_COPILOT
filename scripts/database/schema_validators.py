"""Schema validation helpers for asset ingestion.

These helpers ensure that the target database has the expected tables and
columns before any ingestion takes place. They also perform a quick integrity
check using ``PRAGMA quick_check``. The table definitions are sourced from
``unified_database_initializer.TABLES`` to avoid duplication.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from scripts.database.unified_database_initializer import TABLES


def _expected_columns(table: str) -> list[str]:
    """Return the column names defined for ``table``."""

    create_stmt = TABLES[table]
    cols_section = re.search(r"\((.*)\)", create_stmt, re.DOTALL)
    if not cols_section:
        return []
    raw_cols = cols_section.group(1).split(",")
    return [c.strip().split()[0].strip('"') for c in raw_cols if c.strip()]


def _ensure_schema(db_path: Path, table: str) -> None:
    """Ensure ``table`` exists in ``db_path`` with all expected columns."""

    with sqlite3.connect(db_path, isolation_level=None) as conn:
        res = conn.execute("PRAGMA quick_check").fetchone()
        if not res or res[0] != "ok":
            raise RuntimeError(f"integrity check failed for {db_path}")

        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()
        if not row:
            raise RuntimeError(f"missing table: {table}")

        existing = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        expected = set(_expected_columns(table))
        missing = expected - existing
        if missing:
            raise RuntimeError(f"table {table} missing columns: {', '.join(sorted(missing))}")


def ensure_documentation_schema(db_path: Path) -> None:
    _ensure_schema(db_path, "documentation_assets")


def ensure_template_schema(db_path: Path) -> None:
    _ensure_schema(db_path, "template_assets")


def ensure_har_schema(db_path: Path) -> None:
    _ensure_schema(db_path, "har_entries")


__all__ = [
    "ensure_documentation_schema",
    "ensure_template_schema",
    "ensure_har_schema",
]

