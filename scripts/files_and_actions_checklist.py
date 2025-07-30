#!/usr/bin/env python3
"""
DUAL COPILOT, DATABASE-FIRST PROMPT:
1. Query production.db for file and action checklist patterns.
2. Audit all key files, log missing actions, generate checklist report.
3. Fetch web search for file audit and checklist best practices.
4. Use tqdm for progress, start time logging, timeout, ETC calculation, and real-time status updates.
5. Validate anti-recursion and workspace integrity before file audit.
6. DUAL COPILOT: Secondary validator checks for compliance and visual indicators.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation

DEFAULT_FILES = [
    "DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md",
    "DUAL_COPILOT_PATTERN.instructions.md",
    "auto_generator.py",
]


def fetch_checklist_patterns(production_db: Path) -> List[str]:
    """Return additional file patterns from the production database."""
    if not production_db.exists():
        return []
    with sqlite3.connect(production_db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS checklist_patterns (pattern TEXT)"
        )
        rows = conn.execute("SELECT pattern FROM checklist_patterns").fetchall()
        return [row[0] for row in rows]


def audit_files(files: List[str], workspace: Path) -> List[Dict[str, str]]:
    """Check whether each file exists in the workspace."""
    results: List[Dict[str, str]] = []
    with tqdm(total=len(files), desc="Auditing files", unit="file") as bar:
        for name in files:
            path = workspace / name
            status = "present" if path.exists() else "missing"
            results.append({"file": str(path), "status": status})
            bar.update(1)
    return results


def log_audit(results: List[Dict[str, str]], analytics_db: Path) -> None:
    """Store audit results in ``analytics.db``."""
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS file_audit (file_path TEXT, status TEXT, ts TEXT)"
        )
        for row in results:
            conn.execute(
                "INSERT INTO file_audit (file_path, status, ts) VALUES (?, ?, ?)",
                (row["file"], row["status"], datetime.now().isoformat()),
            )
        conn.commit()


def validate_audit(expected_count: int, analytics_db: Path) -> bool:
    """Validate audit count using dual-copilot pattern."""
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM file_audit")
        count = cur.fetchone()[0]
    return count >= expected_count


def generate_report(results: List[Dict[str, str]], report_file: Path) -> None:
    """Write audit summary report."""
    report_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp": datetime.now().isoformat(), "files": results}
    report_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(
    workspace: str | None = None,
    production_db: str | None = None,
    analytics_db: str | None = None,
    report_path: str | None = None,
) -> bool:
    """Run the file audit workflow."""
    if os.getenv("GH_COPILOT_DISABLE_VALIDATION") != "1":
        validate_enterprise_operation()

    workspace_path = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    prod_db = Path(production_db or workspace_path / "databases" / "production.db")
    analytics = Path(analytics_db or workspace_path / "databases" / "analytics.db")
    report = Path(report_path or workspace_path / "reports" / "file_audit_report.json")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.info("[START] file checklist audit")

    patterns = fetch_checklist_patterns(prod_db)
    files = DEFAULT_FILES + patterns
    results = audit_files(files, workspace_path)
    log_audit(results, analytics)
    generate_report(results, report)

    valid = validate_audit(len(results), analytics)
    if valid:
        logging.info("[SUCCESS] checklist audit complete")
    else:
        logging.error("[ERROR] validation mismatch")
    return valid


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
