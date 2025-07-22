"""
Compliance Report Generator - Summarize lint and test results.

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Database-first architecture
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
}


def parse_ruff_output(output: str) -> Dict[str, int]:
    """Parse ruff output and count issues."""
    lines = [line for line in output.splitlines() if line.strip() and ":" in line]
    return {"issues": len(lines)}


def parse_pytest_report(path: Path) -> Dict[str, int]:
    """Parse pytest JSON report."""
    if not path.exists():
        return {"tests": 0, "passed": 0, "failed": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        return {
            "tests": summary.get("total", 0),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
        }
    except Exception:
        return {"tests": 0, "passed": 0, "failed": 0}


def generate_compliance_report(
    ruff_file: Path,
    pytest_file: Path,
    output_dir: Path,
    analytics_db: Path,
) -> Dict[str, Any]:
    """Generate JSON and Markdown compliance reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ruff_metrics = (
        parse_ruff_output(ruff_file.read_text(encoding="utf-8"))
        if ruff_file.exists()
        else {"issues": 0}
    )
    pytest_metrics = parse_pytest_report(pytest_file)
    timestamp = datetime.now().isoformat()
    summary = {
        "timestamp": timestamp,
        "ruff": ruff_metrics,
        "pytest": pytest_metrics,
    }

    json_path = output_dir / "compliance_report.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_path = output_dir / "compliance_report.md"
    with open(md_path, "w", encoding="utf-8") as md:
        md.write("# Compliance Report\n\n")
        md.write(f"Generated: {timestamp}\n\n")
        md.write("## Ruff\n")
        md.write(f"- Issues: {ruff_metrics['issues']}\n")
        md.write("\n## Pytest\n")
        md.write(f"- Total: {pytest_metrics['tests']}\n")
        md.write(f"- Passed: {pytest_metrics['passed']}\n")
        md.write(f"- Failed: {pytest_metrics['failed']}\n")

    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT,
                timestamp TEXT,
                metrics TEXT,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.execute(
            "INSERT INTO code_quality_metrics (operation, timestamp, metrics) VALUES (?, ?, ?)",
            ("compliance_report", timestamp, json.dumps(summary)),
        )
        conn.commit()

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate compliance report")
    parser.add_argument("--ruff", type=Path, required=True, help="Ruff output file")
    parser.add_argument("--pytest", type=Path, required=True, help="Pytest JSON report")
    parser.add_argument(
        "--output", type=Path, default=Path("validation"), help="Output directory"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("databases") / "analytics.db",
        help="Analytics database path",
    )
    args = parser.parse_args()

    print(TEXT_INDICATORS["start"], "Generating compliance report")
    result = generate_compliance_report(args.ruff, args.pytest, args.output, args.db)
    print(TEXT_INDICATORS["success"], json.dumps(result, indent=2))
