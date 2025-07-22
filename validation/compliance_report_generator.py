from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


def _parse_ruff(path: Path) -> Dict[str, Any]:
    issues = 0
    for line in path.read_text().splitlines():
        if line.strip():
            issues += 1
    return {"issues": issues}


def _parse_pytest(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    summary = data.get("summary", {})
    return {
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
    }


def generate_compliance_report(
    ruff_file: Path,
    pytest_file: Path,
    output_dir: Path,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> Dict[str, Any]:
    """Compile results from ruff and pytest runs into reports."""
    ruff_metrics = _parse_ruff(ruff_file)
    pytest_metrics = _parse_pytest(pytest_file)
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "ruff": ruff_metrics,
        "pytest": pytest_metrics,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "compliance_report.json"
    md_path = output_dir / "compliance_report.md"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write("# Compliance Report\n\n")
        md.write(f"**Timestamp:** {summary['timestamp']}\n\n")
        md.write(f"## Ruff Issues: {ruff_metrics['issues']}\n")
        md.write(
            f"## Pytest Results: {pytest_metrics['passed']} passed / {pytest_metrics['failed']} failed of {pytest_metrics['total']} total\n"
        )

    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruff_issues INTEGER,
                tests_passed INTEGER,
                tests_failed INTEGER,
                ts TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO code_quality_metrics (ruff_issues, tests_passed, tests_failed, ts) VALUES (?, ?, ?, ?)",
            (
                ruff_metrics["issues"],
                pytest_metrics["passed"],
                pytest_metrics["failed"],
                summary["timestamp"],
            ),
        )
        conn.commit()
    return summary

__all__ = ["generate_compliance_report"]
