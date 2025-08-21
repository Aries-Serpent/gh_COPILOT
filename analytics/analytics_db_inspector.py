"""Utilities for recording governance check results."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3

DB_PATH = Path("databases/analytics.db")


def record_governance_check(check: str, status: str, db_path: Path = DB_PATH) -> None:
    """Insert a governance check result into the analytics database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS governance_checks (\"check\" TEXT, status TEXT, timestamp TEXT)"
        )
        cur.execute(
            "INSERT INTO governance_checks (\"check\", status, timestamp) VALUES (?, ?, ?)",
            (check, status, datetime.utcnow().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
