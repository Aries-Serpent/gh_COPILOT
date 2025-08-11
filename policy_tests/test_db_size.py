"""Governance policy tests for database size limits."""
from __future__ import annotations

from pathlib import Path

MAX_BYTES = 100 * 1024 * 1024  # 100 MB


def test_databases_within_size() -> None:
    """Ensure tracked SQLite databases remain under the size limit."""
    db_dir = Path("databases")
    for db_file in db_dir.glob("*.db"):
        size = db_file.stat().st_size
        assert size < MAX_BYTES, f"{db_file.name} exceeds {MAX_BYTES} bytes"
