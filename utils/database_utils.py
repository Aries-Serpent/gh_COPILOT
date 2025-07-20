"""Database utilities for gh_COPILOT Enterprise Toolkit"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


@contextmanager
def get_enterprise_database_connection(db_name: str = "production.db") -> Iterator[sqlite3.Connection]:
    """Get enterprise database connection with proper handling"""
    workspace = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
    db_path = Path(workspace) / "databases" / db_name

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()


def execute_safe_query(query: str, params: tuple = (), db_name: str = "production.db") -> Optional[list]:
    """Execute database query safely"""
    try:
        with get_enterprise_database_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception:
        return None


def check_table_exists(table_name: str, db_name: str = "production.db") -> bool:
    """Check if table exists in database"""
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = execute_safe_query(query, (table_name,), db_name)
    return bool(result)
