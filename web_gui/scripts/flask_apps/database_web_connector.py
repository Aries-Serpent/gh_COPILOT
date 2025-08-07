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
        except sqlite3.Error as exc:  # pragma: no cover - runtime safeguard
            self.logger.error("database connection error: %s", exc)
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple | None = None) -> List[sqlite3.Row]:
        """Execute *query* safely and return all rows.

        Any database errors are logged and result in an empty list, allowing the
        web layer to continue operating without exposing internal errors.
        """
        try:
            with self.get_database_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, params or ())
                return cur.fetchall()
        except sqlite3.Error as exc:
            self.logger.error("query failed: %s", exc)
            return []

    def fetch_enterprise_metrics(self) -> List[Dict[str, Any]]:
        """Return all enterprise metrics records."""
        query = "SELECT metric_name, metric_value FROM enterprise_metrics"
        rows = self.execute_query(query)
        return [{"metric_name": r[0], "metric_value": r[1]} for r in rows]

    def fetch_recent_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent script activity."""
        query = "SELECT script_name, last_modified FROM tracked_scripts ORDER BY last_modified DESC LIMIT ?"
        rows = self.execute_query(query, (limit,))
        return [{"script_name": r[0], "last_modified": r[1]} for r in rows]

    def fetch_compliance_summary(self) -> Dict[str, Any]:
        """Return the latest compliance scan summary."""
        query = (
            "SELECT compliance_score, total_files, non_compliant_files, scan_timestamp "
            "FROM compliance_scans ORDER BY scan_timestamp DESC LIMIT 1"
        )
        rows = self.execute_query(query)
        row = rows[0] if rows else None
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
        rows = self.execute_query(query, (limit,))
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
        rows = self.execute_query(query, (limit,))
        return [
            {
                "file_path": r[0],
                "violation_code": r[1],
                "timestamp": r[2],
            }
            for r in rows
        ]

    def fetch_dashboard_alerts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent dashboard alerts if available."""
        query = (
            "SELECT alert_type, alert_message, created_at "
            "FROM dashboard_alerts ORDER BY created_at DESC LIMIT ?"
        )
        rows = self.execute_query(query, (limit,))
        return [
            {
                "alert_type": r[0],
                "alert_message": r[1],
                "timestamp": r[2],
            }
            for r in rows
        ]

    def fetch_zero_byte_logs(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return logs related to zero-byte file detections."""
        query = (
            "SELECT file_path, detected_at FROM zero_byte_logs ORDER BY detected_at DESC LIMIT ?"
        )
        rows = self.execute_query(query, (limit,))
        return [
            {
                "file_path": r[0],
                "timestamp": r[1],
            }
            for r in rows
        ]
