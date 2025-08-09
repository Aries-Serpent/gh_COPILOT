"""Ingest ruff + pytest JSON outputs into analytics.db."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

from scripts.compliance.update_compliance_metrics import (
    _ensure_metrics_table,
    _ensure_table,
)

RUFF_JSON = Path("ruff_report.json")
PYTEST_JSON = Path(".report.json")  # default name from pytest --json-report


def _db(workspace: Optional[str] = None) -> Path:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    return ws / "databases" / "analytics.db"


def ingest(
    workspace: Optional[str] = None,
    ruff_json: Optional[Path] = None,
    pytest_json: Optional[Path] = None,
) -> None:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db_path = _db(workspace)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    ruff_path = ruff_json or ws / RUFF_JSON
    pytest_path = pytest_json or ws / PYTEST_JSON
    with sqlite3.connect(db_path) as conn:
        _ensure_table(conn)
        _ensure_metrics_table(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ruff_issue_log (
                run_timestamp INTEGER DEFAULT (STRFTIME('%s','now')),
                issues INTEGER
            )
            """
        )
        issues = 0
        if ruff_path.exists():
            try:
                data = json.loads(ruff_path.read_text(encoding="utf-8"))
                issues = len(data) if isinstance(data, list) else int(data.get("issue_count", 0))
            except Exception:
                issues = 0
            conn.execute("INSERT INTO ruff_issue_log(issues) VALUES(?)", (issues,))
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_run_stats (
                run_timestamp INTEGER DEFAULT (STRFTIME('%s','now')),
                passed INTEGER,
                total INTEGER
            )
            """
        )
        passed = total = 0
        if pytest_path.exists():
            try:
                data = json.loads(pytest_path.read_text(encoding="utf-8"))
                summary = data.get("summary", {})
                total = int(summary.get("total", 0))
                passed = int(summary.get("passed", 0))
            except Exception:
                total = passed = 0
            conn.execute("INSERT INTO test_run_stats(passed,total) VALUES(?,?)", (passed, total))
        L = max(0.0, 100.0 - float(issues))
        T = (float(passed) / total * 100.0) if total else 0.0
        composite = 0.3 * L + 0.5 * T  # placeholder score assumed 0 for now
        ts = int(time.time())
        conn.execute(
            """
            INSERT INTO compliance_metrics_history (
                ts, ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved,
                lint_score, test_score, placeholder_score,
                composite_score, source, meta_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (ts, issues, passed, total, None, None, L, T, None, composite, "ingest_pipeline", None),
        )
        conn.execute(
            """
            INSERT INTO compliance_scores (
                timestamp, L, T, P, composite,
                ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (ts, L, T, 0.0, composite, issues, passed, total, 0, 0),
        )
        conn.commit()


if __name__ == "__main__":  # pragma: no cover
    ingest()
