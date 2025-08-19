from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import subprocess
import sys
import importlib.util


SPEC_PATH = Path("scripts/audit/audit_report_generator.py")
spec = importlib.util.spec_from_file_location("audit_report_generator", SPEC_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)
generate_audit_report = module.generate_audit_report


def _prepare_db(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE violation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            details TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE code_quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruff_issues INTEGER,
            tests_passed INTEGER,
            tests_failed INTEGER,
            placeholders_open INTEGER,
            placeholders_resolved INTEGER,
            lint_score REAL,
            test_score REAL,
            placeholder_score REAL,
            composite_score REAL,
            ts TEXT NOT NULL
            )"""
        )
        conn.execute(
            "INSERT INTO violation_logs (timestamp, details) VALUES (?, ?)",
            ("2025-08-18T00:00:00", "test violation"),
        )
        conn.execute(
            """INSERT INTO code_quality_metrics (
            ruff_issues, tests_passed, tests_failed, placeholders_open,
            placeholders_resolved, lint_score, test_score, placeholder_score,
            composite_score, ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (1, 5, 0, 2, 1, 0.8, 1.0, 0.5, 0.9, "2025-08-18T00:00:00"),
        )


def test_generate_audit_report(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    _prepare_db(db)
    out = tmp_path / "report"
    summary = generate_audit_report(db, out)
    assert (out.with_suffix(".json")).exists()
    assert (out.with_suffix(".md")).exists()
    assert summary["violations"][0]["details"] == "test violation"
    data = json.loads(out.with_suffix(".json").read_text())
    assert data["metrics"]["tests_passed"] == 5


def test_cli_execution(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    _prepare_db(db)
    out = tmp_path / "cli_report"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit/audit_report_generator.py",
            "--analytics-db",
            str(db),
            "--output",
            str(out),
        ],
        check=True,
    )
    assert out.with_suffix(".md").exists()
    assert out.with_suffix(".json").exists()
