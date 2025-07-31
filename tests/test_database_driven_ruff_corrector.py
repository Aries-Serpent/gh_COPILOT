#!/usr/bin/env python3
import sqlite3
import subprocess
from pathlib import Path

from scripts.database.database_driven_ruff_corrector import DatabaseDrivenRuffCorrector


def _setup_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE correction_history (id INTEGER PRIMARY KEY, file_path TEXT, violation_code TEXT, original_line TEXT, corrected_line TEXT, correction_timestamp TEXT)"
        )
        conn.execute(
            "CREATE TABLE correction_progress (id INTEGER PRIMARY KEY CHECK (id=1), last_file_index INTEGER NOT NULL, total_files INTEGER NOT NULL, updated_at TEXT NOT NULL)"
        )


def test_ruff_corrector_records_history(tmp_path, monkeypatch):
    db_path = tmp_path / "prod.db"
    _setup_db(db_path)

    py_file = tmp_path / "bad.py"
    py_file.write_text("x=1  \n", encoding="utf-8")

    calls = []

    def fake_run(cmd, *a, **kw):
        calls.append(cmd)

        class R:
            def __init__(self):
                self.returncode = 0
                if cmd[:3] == ["ruff", "check", str(py_file)]:
                    self.stdout = f"{py_file}:1:1: F401 x unused variable"
                else:
                    self.stdout = ""
                if cmd and cmd[0] == "autopep8":
                    Path(cmd[-1]).write_text("x = 1\n", encoding="utf-8")

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "scripts.database.database_driven_ruff_corrector.EnterpriseFlake8Corrector.cross_validate_with_ruff",
        lambda self, tmp, orig: True,
    )
    monkeypatch.setattr(
        "scripts.database.database_driven_ruff_corrector.SecondaryCopilotValidator.validate_corrections",
        lambda self, files: True,
    )

    corrector = DatabaseDrivenRuffCorrector(workspace_path=str(tmp_path), db_path=str(db_path))
    assert corrector.execute_correction()
    assert any("--fix" in cmd for cmd in calls)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT corrected_line FROM correction_history").fetchall()
    assert rows and rows[0][0] == "x = 1"
