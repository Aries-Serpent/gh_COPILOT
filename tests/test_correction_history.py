#!/usr/bin/env python3
import logging
import shutil
import sqlite3
from pathlib import Path

from scripts.database.database_first_windows_compatible_flake8_corrector import (
    CorrectionPattern, DatabaseFirstFlake8Corrector, FlakeViolation)


def test_correction_history_records(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()

    # copy analytics.db and run migration
    src_db = repo_root / "databases" / "analytics.db"
    dest_db = db_dir / "analytics.db"
    shutil.copy(src_db, dest_db)

    migration_sql = (
        repo_root / "databases" / "migrations" / "add_correction_history.sql"
    ).read_text()
    with sqlite3.connect(dest_db) as conn:
        conn.execute("ALTER TABLE violations ADD COLUMN session_id TEXT")
        conn.executescript(migration_sql)
        try:
            conn.execute("ALTER TABLE violations ADD COLUMN session_id TEXT")
        except sqlite3.OperationalError:
            pass

    # prepare file with trailing whitespace violation
    test_file = workspace / "example.py"
    test_file.write_text("print('hi') \n")

    corrector = DatabaseFirstFlake8Corrector(workspace_path=str(workspace))
    corrector.analytics_db = str(dest_db)
    corrector.correction_patterns["W293"] = CorrectionPattern(
        pattern_id="test",
        error_code="W293",
        pattern_regex="",
        replacement_template="",
        confidence_score=1.0,
        success_rate=1.0,
        usage_count=0,
    )

    violation = FlakeViolation(
        file_path=str(test_file),
        line_number=1,
        column=1,
        error_code="W293",
        message="trailing whitespace",
    )
    result = corrector.apply_correction_pattern(str(test_file), violation)

    corrector.save_correction_results_to_database([violation], [result])

    with sqlite3.connect(dest_db) as conn:
        rows = conn.execute(
            "SELECT file_path, violation_code, fix_applied FROM correction_history"
        ).fetchall()

    assert rows, "Correction history not recorded"
    assert len(rows) == len(result.violations_fixed)
