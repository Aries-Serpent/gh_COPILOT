from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List

__all__ = ["DatabaseWebConnector"]


class DatabaseWebConnector:
    """Database-Driven Web Component Engine."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_database_connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def fetch_enterprise_metrics(self) -> List[Dict[str, Any]]:
        """Return all enterprise metrics records."""
        query = "SELECT metric_name, metric_value FROM enterprise_metrics"
        with self.get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
        return [{"metric_name": r[0], "metric_value": r[1]} for r in rows]

    def fetch_recent_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent script activity."""
        query = "SELECT script_name, last_modified FROM tracked_scripts ORDER BY last_modified DESC LIMIT ?"
        with self.get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (limit,))
            rows = cur.fetchall()
        return [{"script_name": r[0], "last_modified": r[1]} for r in rows]
