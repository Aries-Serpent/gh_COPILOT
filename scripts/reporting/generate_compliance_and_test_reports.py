#!/usr/bin/env python3
"""Generate compliance, test, and lint reports."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "databases" / "analytics.db"
OUTPUT_DIR = ROOT / "documentation" / "generated" / "daily state update"


def _query_counts(db: Path) -> dict[str, int]:
    """Return counts of placeholder, forbidden-command, and anti-recursion findings."""
    queries = {
        "placeholders": "SELECT COUNT(*) FROM placeholder_removals",
        "forbidden_commands": "SELECT COUNT(*) FROM violation_logs WHERE details LIKE '%forbidden%'",
        "anti_recursions": "SELECT COUNT(*) FROM violation_logs WHERE details LIKE '%anti-recursion%'",
    }
    counts = {}
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        for key, sql in queries.items():
            try:
                counts[key] = cur.execute(sql).fetchone()[0]
            except sqlite3.Error:
                counts[key] = 0
    return counts


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run a command and return its exit code and combined output."""
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd
    )
    output = proc.stdout.strip()
    return proc.returncode, output


def generate_reports() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    counts = _query_counts(DB_PATH)

    pytest_rc, pytest_out = _run(["pytest", "-q"], cwd=ROOT)
    pytest_summary = pytest_out.splitlines()[-1] if pytest_out else ""

    ruff_rc, ruff_out = _run(
        [
            "ruff",
            "check",
            ".",
            "--quiet",
            "--config",
            str(ROOT / "pyproject.toml"),
            "--force-exclude",
        ],
        cwd=ROOT,
    )
    lint_errors = len(ruff_out.splitlines()) if ruff_rc else 0

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = {
        "timestamp": timestamp,
        "compliance": counts,
        "tests": {"exit_code": pytest_rc, "summary": pytest_summary},
        "lint": {"exit_code": ruff_rc, "errors": lint_errors},
    }

    md_lines = [
        f"# Daily State Update ({timestamp})",
        "",
        "## Compliance Findings",
        f"- Placeholder removals: {counts['placeholders']}",
        f"- Forbidden command violations: {counts['forbidden_commands']}",
        f"- Anti-recursion violations: {counts['anti_recursions']}",
        "",
        "## Test Results",
        f"- pytest: {pytest_summary or 'no output'} (exit code {pytest_rc})",
        "",
        "## Lint Results",
        f"- ruff: {'passed' if ruff_rc == 0 else f'{lint_errors} issues'} (exit code {ruff_rc})",
        "",
    ]
    md_path = OUTPUT_DIR / f"daily_state_{timestamp}.md"
    json_path = OUTPUT_DIR / f"daily_state_{timestamp}.json"
    md_path.write_text("\n".join(md_lines))
    json_path.write_text(json.dumps(data, indent=2))
    return data


def main() -> None:
    generate_reports()


if __name__ == "__main__":
    main()
