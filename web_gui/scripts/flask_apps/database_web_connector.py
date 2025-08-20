from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, Iterator, List, Sequence

__all__ = ["DatabaseWebConnector"]


class DatabaseWebConnector:
    """Database-Driven Web Component Engine."""

    def __init__(self, db_path: Path | str, pool_size: int = 5) -> None:
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._pool_size = pool_size
        self._pool: Queue[sqlite3.Connection] = Queue(maxsize=pool_size)

    @contextmanager
    def get_database_connection(self) -> Iterator[sqlite3.Connection]:
        try:
            conn = self._pool.get_nowait()
        except Empty:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            yield conn
        except sqlite3.Error as exc:  # pragma: no cover - runtime safeguard
            self.logger.error("database connection error: %s", exc)
            raise
        finally:
            try:
                self._pool.put_nowait(conn)
            except Exception:
                conn.close()

    # ------------------------------------------------------------------
    # Generic Database Helpers
    # ------------------------------------------------------------------
    def execute_query(
        self, query: str, params: Sequence[Any] | None = None
    ) -> List[sqlite3.Row]:
        """Execute a SQL query with optional parameters.

        Returns an empty list when execution fails.
        """

        params = params or []
        with self.get_database_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute(query, params)
                return cur.fetchall()
            except sqlite3.Error as exc:
                self.logger.error("query failed: %s", exc)
                return []

    def fetch_enterprise_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Return enterprise metrics including their measurement units."""
        rows = self.execute_query(
            "SELECT metric_name, metric_value, metric_unit FROM enterprise_metrics"
        )
        return {
            r["metric_name"]: {
                "value": r["metric_value"],
                "unit": r["metric_unit"],
            }
            for r in rows
        }

    def fetch_recent_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent script activity."""
        query = (
            "SELECT script_name, last_modified "
            "FROM tracked_scripts ORDER BY last_modified DESC LIMIT ?"
        )
        rows = self.execute_query(query, (limit,))
        return [
            {"script_name": r["script_name"], "last_modified": r["last_modified"]}
            for r in rows
        ]

    def fetch_compliance_summary(self) -> Dict[str, Any]:
        """Return the latest compliance scan summary."""
        query = (
            "SELECT compliance_score, total_files, non_compliant_files, scan_timestamp "
            "FROM compliance_scans ORDER BY scan_timestamp DESC LIMIT 1"
        )
        rows = self.execute_query(query)
        row = rows[0] if rows else None
        if row is None:
            return {}
        return {
            "compliance_score": row["compliance_score"],
            "total_files": row["total_files"],
            "non_compliant_files": row["non_compliant_files"],
            "timestamp": row["scan_timestamp"],
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
                "sequence_id": r["sequence_id"],
                "status": r["status"],
                "started": r["execution_start"],
                "ended": r["execution_end"],
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
                "file_path": r["file_path"],
                "violation_code": r["violation_code"],
                "timestamp": r["correction_timestamp"],
            }
            for r in rows
        ]

    def fetch_latest_system_metrics(self) -> Dict[str, Any]:
        """Return the most recent system monitoring metrics."""
        query = (
            "SELECT timestamp, cpu_usage, memory_usage, disk_usage, "
            "enterprise_readiness, anomalies_detected, metrics_json "
            "FROM system_monitoring_live ORDER BY timestamp DESC LIMIT 1"
        )
        with self.get_database_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute(query)
                row = cur.fetchone()
            except sqlite3.Error as exc:
                self.logger.error("system metrics fetch error: %s", exc)
                return {}
        if row is None:
            return {}
        data = dict(row)
        try:
            data["metrics_json"] = json.loads(data.get("metrics_json") or "{}")
        except json.JSONDecodeError:
            data["metrics_json"] = {}
        return data

    def fetch_latest_performance_metrics(self) -> Dict[str, Any]:
        """Return the most recent performance metrics."""
        query = (
            "SELECT operation_type, execution_time, files_processed, "
            "success_rate, memory_usage, system_resources "
            "FROM performance_metrics ORDER BY timestamp DESC LIMIT 1"
        )
        with self.get_database_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute(query)
                row = cur.fetchone()
            except sqlite3.Error as exc:
                self.logger.error("performance metrics fetch error: %s", exc)
                return {}
        if row is None:
            return {}
        data = dict(row)
        try:
            data["system_resources"] = json.loads(
                data.get("system_resources") or "{}"
            )
        except json.JSONDecodeError:
            data["system_resources"] = {}
        return data

    def fetch_dashboard_alerts(self) -> List[Dict[str, Any]]:
        """Return dashboard alerts if the table exists."""
        query = (
            "SELECT alert_type, alert_message, created_at "
            "FROM dashboard_alerts ORDER BY created_at DESC"
        )
        rows = self.execute_query(query)
        return [
            {
                "alert_type": r["alert_type"],
                "alert_message": r["alert_message"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def fetch_zero_byte_logs(self) -> List[Dict[str, Any]]:
        """Return logged zero-byte file incidents."""
        query = (
            "SELECT file_path, detected_at "
            "FROM zero_byte_logs ORDER BY detected_at DESC"
        )
        rows = self.execute_query(query)
        return [
            {"file_path": r["file_path"], "detected_at": r["detected_at"]}
            for r in rows
        ]

    def close_pool(self) -> None:
        """Close all pooled connections."""
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            conn.close()
