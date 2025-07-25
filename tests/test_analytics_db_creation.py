"""Validate analytics.db migrations can run in a fresh database.

This test ensures the migrations in ``databases/migrations`` can be
applied to create the ``analytics.db`` schema. The repository includes an
``analytics.db`` file, but it should be possible to recreate it from the
SQL migrations when needed. The test does not rely on the existing file
and runs entirely in a temporary directory.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def test_analytics_db_creation(tmp_path: Path) -> None:
    """Run migrations and verify required tables exist."""

    repo_root = Path(__file__).resolve().parents[1]
    analytics = tmp_path / "analytics.db"

    migration_dir = repo_root / "databases" / "migrations"
    code_audit_sql = (migration_dir / "add_code_audit_log.sql").read_text()
    correction_history_sql = (migration_dir / "add_correction_history.sql").read_text()

    with sqlite3.connect(analytics) as conn:
        conn.executescript(code_audit_sql)
        conn.executescript(correction_history_sql)

    with sqlite3.connect(analytics) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert "code_audit_log" in tables
    assert "correction_history" in tables

