#!/usr/bin/env python3
"""Generate audit reports from ``analytics.db``.

This utility reads recent violations and the latest code quality metrics
from a SQLite database and emits both Markdown and JSON summaries.  The
output path is provided via CLI option and is used as the base name for
the two generated files (``.md`` and ``.json``).
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


def _collect_summary(db_path: Path) -> Dict[str, Any]:
    """Return recent violations and latest metrics from ``db_path``.

    The function tolerates missing tables and returns empty collections if
    the database is absent or lacks the expected schema.
    """

    if not db_path.exists():
        return {"violations": [], "metrics": {}}

    violations: List[Dict[str, str]] = []
    metrics: Dict[str, Any] = {}

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(
                    "SELECT timestamp, details FROM violation_logs ORDER BY timestamp DESC LIMIT 5"
                ).fetchall()
                violations = [{"timestamp": r["timestamp"], "details": r["details"]} for r in rows]
            except sqlite3.Error:
                violations = []

            try:
                row = conn.execute(
                    "SELECT * FROM code_quality_metrics ORDER BY id DESC LIMIT 1"
                ).fetchone()
                if row:
                    metrics = dict(row)
            except sqlite3.Error:
                metrics = {}
    except sqlite3.Error:
        return {"violations": [], "metrics": {}}

    return {"violations": violations, "metrics": metrics}


def generate_audit_report(analytics_db: Path, output: Path) -> Dict[str, Any]:
    """Create audit summaries from ``analytics_db`` and write to ``output``.

    ``output`` should be a path without an extension; ``.json`` and ``.md``
    versions of the report will be created.
    """

    summary = _collect_summary(analytics_db)
    output.parent.mkdir(parents=True, exist_ok=True)

    json_path = output.with_suffix(".json")
    md_path = output.with_suffix(".md")

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = ["# Audit Report"]
    violations = summary.get("violations", [])
    if violations:
        lines.append("## Recent Violations")
        for item in violations:
            lines.append(f"- {item['timestamp']}: {item['details']}")
    else:
        lines.extend(["## Recent Violations", "None"])

    metrics = summary.get("metrics", {})
    if metrics:
        lines.append("## Latest Metrics")
        for key, value in metrics.items():
            lines.append(f"- **{key}**: {value}")
    else:
        lines.extend(["## Latest Metrics", "None"])

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return summary


def _parse_args(argv: List[str] | None = None) -> Namespace:
    parser = ArgumentParser(description="Generate audit reports from analytics.db")
    parser.add_argument(
        "--analytics-db",
        type=Path,
        default=Path("analytics.db"),
        help="Path to analytics.db",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Base path for generated reports (without extension)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv)
    generate_audit_report(args.analytics_db, args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
