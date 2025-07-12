import sqlite3
from pathlib import Path

from database_driven_flake8_corrector_functional import \
    DatabaseDrivenFlake8CorrectorFunctional


def test_corrector_records_corrections(tmp_path):
    db_path = tmp_path / "prod.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE correction_history (id INTEGER PRIMARY KEY, file_path TEXT, violation_code TEXT, original_line TEXT, corrected_line TEXT, correction_timestamp TEXT)"
        )
    py_file = tmp_path / "bad.py"
    py_file.write_text("print('hi')  \n")

    corrector = DatabaseDrivenFlake8CorrectorFunctional(
        workspace_path=str(tmp_path), db_path=str(db_path))
    success = corrector.execute_correction()
    assert success
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM correction_history").fetchone()
    assert row[0] >= 1
