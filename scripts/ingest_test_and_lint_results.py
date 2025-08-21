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
from scripts.placeholder_snapshot import get_latest_placeholder_snapshot

RUFF_JSON = Path("ruff_report.json")
PYTEST_JSON = Path(".report.json")  # default name from pytest --json-report


def _db(workspace: Optional[str] = None) -> Path:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    return ws / "databases" / "analytics.db"


def _ensure_db_path(db_path: Path) -> None:
    """Ensure the database path and parent directories exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("SELECT 1")


def ingest(
    workspace: Optional[str] = None,
    ruff_json: Optional[Path] = None,
    pytest_json: Optional[Path] = None,
) -> int:
    """
    Ingest ruff and pytest JSON outputs into analytics.db,
    populating ruff_issue_log, test_run_stats, compliance_metrics_history, and compliance_scores.
    """
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db_path = _db(workspace)
    _ensure_db_path(db_path)
    ruff_path = ruff_json or ws / RUFF_JSON
    pytest_path = pytest_json or ws / PYTEST_JSON

    with sqlite3.connect(db_path) as conn:
        # Ensure necessary tables for both legacy and current metrics
        _ensure_table(conn)
        _ensure_metrics_table(conn)

        run_ts = int(time.time() * 1000)

        # --- Ruff issues log ---
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
        conn.execute(
            "INSERT INTO ruff_issue_log(run_timestamp, issues) VALUES(?,?)",
            (run_ts, issues),
        )

        # --- Pytest stats ---
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
        conn.execute(
            "INSERT INTO test_run_stats(run_timestamp, passed,total) VALUES(?,?,?)",
            (run_ts, passed, total),
        )

        # --- Compliance metrics ---
        # Retrieve latest placeholder snapshot for placeholder score
        open_ph, resolved_ph = get_latest_placeholder_snapshot(conn)
        L = max(0.0, 100.0 - float(issues))
        T = (float(passed) / total * 100.0) if total else 0.0
        denom = open_ph + resolved_ph
        P = (float(resolved_ph) / denom * 100.0) if denom else 100.0
        composite = 0.3 * L + 0.5 * T + 0.2 * P
        ts = int(time.time())
        # Insert into metrics history (newer normalized table)
        cur = conn.execute(
            """
            INSERT INTO compliance_metrics_history (
                ts, ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved,
                lint_score, test_score, placeholder_score,
                composite_score, source, meta_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (ts, issues, passed, total, open_ph, resolved_ph, L, T, P, composite, "ingest_pipeline", None),
        )
        row_id = cur.lastrowid
        # Insert into legacy compliance_scores table
        conn.execute(
            """
            INSERT INTO compliance_scores (
                timestamp, L, T, P, composite,
                ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved,
                session_score, sessions_successful, sessions_failed
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                L,
                T,
                P,
                composite,
                issues,
                passed,
                total,
                open_ph,
                resolved_ph,
                0.0,
                0,
                0,
            ),
        )
        conn.commit()

    return row_id


if __name__ == "__main__":  # pragma: no cover
    ingest()


__all__ = [
    "_db",
    "_ensure_db_path",
    "ingest",
]
