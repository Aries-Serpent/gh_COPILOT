#!/usr/bin/env python3
import sqlite3

from scripts.database.database_driven_flake8_corrector_functional import \
    DatabaseDrivenFlake8CorrectorFunctional


def test_corrector_records_corrections(tmp_path):
    db_path = tmp_path / "prod.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE correction_history (id INTEGER PRIMARY KEY, \
                file_path TEXT, violation_code TEXT, \
                    original_line TEXT, corrected_line TEXT, correction_timestamp TEXT)"
        )
        conn.execute(
            "CREATE TABLE correction_progress (id INTEGER PRIMARY KEY CHECK (id=1), \
                \
                last_file_index INTEGER NOT NULL, \
                    total_files INTEGER NOT NULL, updated_at TEXT NOT NULL)"
        )
    py_file = tmp_path / "bad.py"
    py_file.write_text("print('hi')  \n")

    corrector = DatabaseDrivenFlake8CorrectorFunctional(
        workspace_path=str(tmp_path), db_path=str(db_path))
    success = corrector.execute_correction()
    assert success
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT original_line, corrected_line FROM correction_history"
        ).fetchall()
    assert rows
    # trailing whitespace removed by autopep8
    assert rows[0][1] == "print('hi')"


def test_unicode_paths_and_progress(tmp_path):
    db_path = tmp_path / "prod.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE correction_history (id INTEGER PRIMARY KEY, \
                file_path TEXT, violation_code TEXT, \
                    original_line TEXT, corrected_line TEXT, correction_timestamp TEXT)"
        )
        conn.execute(
            "CREATE TABLE correction_progress (id INTEGER PRIMARY KEY CHECK (id=1), \
                \
                last_file_index INTEGER NOT NULL, \
                    total_files INTEGER NOT NULL, updated_at TEXT NOT NULL)"
        )

    unicode_dir = tmp_path / "路径"
    unicode_dir.mkdir()
    for i in range(2):
        (unicode_dir / f"file{i}.py").write_text("print('hi')  \n")

    corrector = DatabaseDrivenFlake8CorrectorFunctional(
        workspace_path=str(unicode_dir), db_path=str(db_path)
    )
    assert corrector.execute_correction()

    with sqlite3.connect(db_path) as conn:
        recorded = conn.execute(
            "SELECT file_path, corrected_line FROM correction_history"
        ).fetchall()
        progress = conn.execute(
            "SELECT last_file_index, total_files FROM correction_progress WHERE id=1"
        ).fetchone()

    assert len(recorded) >= 1
    assert all(r[1] == "print('hi')" for r in recorded)
    assert progress == (2, 2)
