"""Database helper utilities with validation checks."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def get_validated_connection(db_name: str = "production.db") -> Iterator[sqlite3.Connection]:
    """Return a validated connection to ``production.db``.

    The helper ensures the database exists and is within the size limit
    before yielding an SQLite connection.
    """
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db_path = workspace / "databases" / db_name

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    size_bytes = db_path.stat().st_size
    if size_bytes == 0:
        raise ValueError(f"Database is empty: {db_path}")
    if size_bytes > 100 * 1024 * 1024:
        raise ValueError(f"Database too large: {db_path}")

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn is not None:
            conn.close()
