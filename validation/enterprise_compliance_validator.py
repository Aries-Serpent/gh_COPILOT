from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from utils.validation_utils import calculate_composite_compliance_score

DEFAULT_DB_PATH = Path("databases/analytics.db")


class EnterpriseComplianceValidator:
    """Aggregate compliance metrics and persist a composite score.

    The validator gathers lint, test, placeholder, and session metrics from
    ``analytics.db``. It computes a composite compliance score using existing
    project utilities and stores the result in the database for later
    consumption by other components.
    """

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    # ------------------------------------------------------------------
    # database helpers
    # ------------------------------------------------------------------
    def _table_exists(self, cur: sqlite3.Cursor, table: str) -> bool:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        return cur.fetchone() is not None

    def _fetch_latest(
        self,
        cur: sqlite3.Cursor,
        table: str,
        columns: str,
        order_by: str = "rowid",
    ) -> Tuple[int, ...]:
        try:
            cur.execute(
                f"SELECT {columns} FROM {table} ORDER BY {order_by} DESC LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                return tuple(int(x or 0) for x in row)
        except sqlite3.Error:
            pass
        return tuple(0 for _ in columns.split(","))

    def _count(self, cur: sqlite3.Cursor, table: str, where: str) -> int:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}")
            row = cur.fetchone()
            return int(row[0]) if row else 0
        except sqlite3.Error:
            return 0

    # ------------------------------------------------------------------
    def aggregate_metrics(self) -> Dict[str, int]:
        """Return aggregated metrics from ``analytics.db``.

        Raises
        ------
        FileNotFoundError
            If the analytics database does not exist.
        """

        if not self.db_path.exists():
            raise FileNotFoundError(f"analytics database not found: {self.db_path}")

        metrics: Dict[str, int] = {
            "lint_issues": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "placeholders_open": 0,
            "placeholders_resolved": 0,
            "sessions": 0,
        }

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # lint issues from ruff_issue_log
            lint, = self._fetch_latest(
                cur, "ruff_issue_log", "issues", order_by="run_timestamp"
            )
            metrics["lint_issues"] = lint

            # test results from test_run_stats
            passed, total = self._fetch_latest(
                cur, "test_run_stats", "passed,total", order_by="run_timestamp"
            )
            metrics["tests_passed"] = passed
            metrics["tests_failed"] = max(0, total - passed)

            # placeholder metrics from todo_fixme_tracking if available
            if self._table_exists(cur, "todo_fixme_tracking"):
                metrics["placeholders_open"] = self._count(
                    cur, "todo_fixme_tracking", "status='open'"
                )
                metrics["placeholders_resolved"] = self._count(
                    cur, "todo_fixme_tracking", "status='resolved'"
                )

            # session metrics from session_lifecycle
            if self._table_exists(cur, "session_lifecycle"):
                cur.execute(
                    "SELECT COUNT(*) FROM session_lifecycle WHERE status='success'"
                )
                row = cur.fetchone()
                metrics["sessions"] = int(row[0]) if row else 0

        return metrics

    def persist_score(self, metrics: Dict[str, int]) -> float:
        """Persist composite compliance score and return it."""

        scores = calculate_composite_compliance_score(
            metrics["lint_issues"],
            metrics["tests_passed"],
            metrics["tests_failed"],
            metrics["placeholders_open"],
            metrics["placeholders_resolved"],
        )
        composite = scores["composite"]

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS enterprise_compliance_scores (
                    timestamp TEXT,
                    lint_issues INTEGER,
                    tests_passed INTEGER,
                    tests_failed INTEGER,
                    placeholders_open INTEGER,
                    placeholders_resolved INTEGER,
                    composite_score REAL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO enterprise_compliance_scores (
                    timestamp, lint_issues, tests_passed, tests_failed,
                    placeholders_open, placeholders_resolved, composite_score
                ) VALUES (?,?,?,?,?,?,?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    metrics["lint_issues"],
                    metrics["tests_passed"],
                    metrics["tests_failed"],
                    metrics["placeholders_open"],
                    metrics["placeholders_resolved"],
                    composite,
                ),
            )
            conn.commit()
        return composite

    def evaluate(self) -> Dict[str, Any]:
        """Aggregate metrics, persist composite score, and return details."""
        metrics = self.aggregate_metrics()
        metrics["composite_score"] = self.persist_score(metrics)
        return metrics


__all__ = ["EnterpriseComplianceValidator"]
