#!/usr/bin/env python3
import logging
import sqlite3
from datetime import datetime, timedelta

<<<<<<< HEAD
from scripts.database.database_first_windows_compatible_flake8_corrector import DatabaseFirstFlake8Corrector
=======
from database_first_windows_compatible_flake8_corrector import \
    DatabaseFirstFlake8Corrector
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_generate_completion_report_logs_once(tmp_path, caplog):
    """Ensure completion report is logged once with summary stats."""
    workspace = tmp_path
    (workspace / "databases").mkdir()

    caplog.set_level(logging.INFO)
    corrector = DatabaseFirstFlake8Corrector(workspace_path=str(workspace))

    start_time = datetime.now() - timedelta(seconds=5)
    with caplog.at_level(logging.INFO):
        corrector.generate_completion_report(start_time)

    messages = [record.message for record in caplog.records]

    assert messages.count("[COMPLETE] DATABASE-FIRST FLAKE8 CORRECTION COMPLETE") == 1
    assert any("Files Processed" in m for m in messages)


def test_secondary_validator_failure_updates_status(tmp_path, monkeypatch):
    """Secondary validation failure marks session as FAILED."""
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
<<<<<<< HEAD
        conn.execute("CREATE TABLE compliance_sessions (session_id TEXT PRIMARY KEY, status TEXT)")
=======
        conn.execute(
            "CREATE TABLE compliance_sessions (session_id TEXT PRIMARY KEY, status TEXT)"
        )
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
        conn.execute(
            "INSERT INTO compliance_sessions (session_id, status) VALUES (?, ?)",
            ("TEST", "COMPLETED"),
        )

    corrector = DatabaseFirstFlake8Corrector(workspace_path=str(workspace))
    corrector.session_id = "TEST"

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        lambda self, files: False,
    )

    monkeypatch.setattr(
        corrector,
        "load_correction_patterns_from_database",
        lambda: None,
    )
<<<<<<< HEAD
    monkeypatch.setattr(corrector, "run_flake8_scan", lambda: [type("V", (), {"file_path": "f.py"})()])
    monkeypatch.setattr(
        corrector,
        "apply_correction_pattern",
        lambda fp, v: type(
            "R",
            (),
            {
                "success": True,
                "violations_fixed": ["E1"],
                "original_content": "",
                "corrected_content": "",
            },
        )(),
    )
=======
    monkeypatch.setattr(corrector, "run_flake8_scan", lambda: [
        type("V", (), {"file_path": "f.py"})()])
    monkeypatch.setattr(corrector, "apply_correction_pattern", lambda fp, v: type(
        "R",
        (),
        {
            "success": True,
            "violations_fixed": ["E1"],
            "original_content": "",
            "corrected_content": "",
        },
    )())
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)

    corrector.execute_comprehensive_correction()

    with sqlite3.connect(analytics_db) as conn:
        status = conn.execute(
            "SELECT status FROM compliance_sessions WHERE session_id='TEST'",
        ).fetchone()[0]
    assert status == "FAILED"
