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

    def fetch_compliance_summary(self) -> Dict[str, Any]:
        """Return the latest compliance scan summary."""
        query = (
            "SELECT compliance_score, total_files, non_compliant_files, scan_timestamp "
            "FROM compliance_scans ORDER BY scan_timestamp DESC LIMIT 1"
        )
        with self.get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            row = cur.fetchone()
        if not row:
            return {}
        return {
            "compliance_score": row[0],
            "total_files": row[1],
            "non_compliant_files": row[2],
            "timestamp": row[3],
        }

    def fetch_rollback_logs(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent recovery execution history as rollback logs."""
        query = (
            "SELECT sequence_id, status, execution_start, execution_end "
            "FROM recovery_execution_history ORDER BY execution_start DESC LIMIT ?"
        )
        with self.get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (limit,))
            rows = cur.fetchall()
        return [
            {
                "sequence_id": r[0],
                "status": r[1],
                "started": r[2],
                "ended": r[3],
            }
            for r in rows
        ]

    def fetch_correction_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent correction history."""
        query = (
            "SELECT file_path, violation_code, correction_timestamp "
            "FROM correction_history ORDER BY correction_timestamp DESC LIMIT ?"
        )
        with self.get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (limit,))
            rows = cur.fetchall()
        return [
            {
                "file_path": r[0],
                "violation_code": r[1],
                "timestamp": r[2],
            }
            for r in rows
        ]
