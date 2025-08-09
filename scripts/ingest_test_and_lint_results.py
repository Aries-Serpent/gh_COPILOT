"""Ingest ruff + pytest JSON outputs into analytics.db."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Optional

RUFF_JSON = Path("ruff_report.json")
PYTEST_JSON = Path(".report.json")  # default name from pytest --json-report


def _db(workspace: Optional[str] = None) -> Path:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    return ws / "databases" / "analytics.db"


def _ensure_db_path(db_path: Path) -> None:
    """Ensure the database path and parent directories exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        # Create empty database file
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("SELECT 1")  # Just create the file


def ingest(
    workspace: Optional[str] = None, 
    ruff_json: Optional[Path] = None, 
    pytest_json: Optional[Path] = None
) -> None:
    db_path = _db(workspace)
    _ensure_db_path(db_path)  # Ensure DB exists before operations
    
    ruff_path = ruff_json or RUFF_JSON
    pytest_path = pytest_json or PYTEST_JSON
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS ruff_issue_log 
            (run_timestamp INTEGER DEFAULT (STRFTIME('%s','now')), 
             issues INTEGER)"""
        )
        if ruff_path.exists():
            try:
                data = json.loads(ruff_path.read_text(encoding="utf-8"))
                issues = len(data) if isinstance(data, list) else int(data.get("issue_count", 0))
            except Exception:
                issues = 0
            conn.execute("INSERT INTO ruff_issue_log(issues) VALUES(?)", (issues,))
        conn.execute(
            """CREATE TABLE IF NOT EXISTS test_run_stats 
            (run_timestamp INTEGER DEFAULT (STRFTIME('%s','now')), 
             passed INTEGER, total INTEGER)"""
        )
        if pytest_path.exists():
            try:
                data = json.loads(pytest_path.read_text(encoding="utf-8"))
                summary = data.get("summary", {})
                total = int(summary.get("total", 0))
                passed = int(summary.get("passed", 0))
            except Exception:
                total = passed = 0
            conn.execute("INSERT INTO test_run_stats(passed,total) VALUES(?,?)", (passed, total))
        conn.commit()
    
    # Trigger compliance metrics update after successful ingestion
    try:
        from scripts.compliance.update_compliance_metrics import update_compliance_metrics
        composite_score = update_compliance_metrics(workspace)
        print(f"✅ Compliance metrics updated: {composite_score:.2f}")
    except Exception as e:
        print(f"⚠️ Failed to update compliance metrics: {e}")


if __name__ == "__main__":  # pragma: no cover
    ingest()
