from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

from enterprise_modules.compliance import _ensure_metrics_table

RUFF_JSON = Path("ruff_report.json")
PYTEST_JSON = Path(".report.json")  # default name from pytest --json-report


def _db(workspace: Optional[str] = None) -> Path:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    return ws / "databases" / "analytics.db"


def ingest(
    workspace: Optional[str] = None,
    ruff_json: Optional[Path] = None,
    pytest_json: Optional[Path] = None,
) -> int:
    db_path = _db(workspace)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    workspace_path = db_path.parent.parent
    ruff_path = ruff_json or workspace_path / RUFF_JSON
    pytest_path = pytest_json or workspace_path / PYTEST_JSON

    ruff_issues = 0
    if ruff_path.exists():
        try:
            data = json.loads(ruff_path.read_text(encoding="utf-8"))
            ruff_issues = len(data) if isinstance(data, list) else int(data.get("issue_count", 0))
        except Exception:
            ruff_issues = 0

    tests_passed = tests_failed = 0
    if pytest_path.exists():
        try:
            data = json.loads(pytest_path.read_text(encoding="utf-8"))
            summary = data.get("summary", {})
            tests_passed = int(summary.get("passed", 0))
            if "failed" in summary:
                tests_failed = int(summary.get("failed", 0))
            else:
                total = int(summary.get("total", 0))
                tests_failed = max(0, total - tests_passed)
        except Exception:
            tests_passed = tests_failed = 0

    with sqlite3.connect(db_path) as conn:
        _ensure_metrics_table(conn)
        cur = conn.execute(
            """
            INSERT INTO compliance_metrics_history (
                timestamp, ruff_issues, tests_passed, tests_failed, placeholders_open, placeholders_resolved
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (int(time.time()), ruff_issues, tests_passed, tests_failed, None, None),
        )
        conn.commit()
        return int(cur.lastrowid)


if __name__ == "__main__":  # pragma: no cover
    ingest()
