from __future__ import annotations

"""Utilities enforcing the database-first workflow."""

import sqlite3
from pathlib import Path
from typing import Optional


def ensure_db_reference(file_path: str, db_path: Optional[str] = None) -> bool:
    """Verify ``file_path`` is tracked in ``production.db`` before modification."""
    db = Path(db_path or Path("databases") / "production.db")
    if not db.exists():
        return False

    try:
        with sqlite3.connect(db) as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM file_registry WHERE path = ?", (file_path,)
            )
            return cur.fetchone()[0] > 0
    except sqlite3.Error:
        return False
