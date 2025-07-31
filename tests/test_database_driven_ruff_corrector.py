from pathlib import Path
import subprocess
import sqlite3

from scripts.database.database_driven_ruff_corrector import DatabaseDrivenRuffCorrector


def _setup_db(db_path: Path) -> None:
    sql = Path("databases/migrations/add_correction_history.sql").read_text()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)


def _create_workspace(tmp_path):
    (tmp_path / "production.db").touch()
    analytics = tmp_path / "analytics.db"
    _setup_db(analytics)
    sample = tmp_path / "sample.py"
    sample.write_text("import os\nprint('hi')  \n", encoding="utf-8")
    return sample, analytics


def test_ruff_corrector_runs_fix(tmp_path, monkeypatch):
    sample, analytics = _create_workspace(tmp_path)
    corrector = DatabaseDrivenRuffCorrector(workspace_path=str(tmp_path), db_path=str(analytics))

    calls = []

    def fake_run(cmd, *a, **kw):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""

        if cmd[:2] == ["ruff", "check"] and "--fix" not in cmd:
            R.stdout = f"{sample}:1:1 F401 unused import os"
        if "--fix" in cmd:
            sample.write_text("import os\nprint('hi')\n", encoding="utf-8")
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(corrector, "validate_corrections", lambda f: True)
    monkeypatch.setattr(corrector.ruff_validator, "cross_validate_with_ruff", lambda f, o: True)

    corrector.execute_correction()

    assert any(cmd[:2] == ["ruff", "check"] and "--fix" in cmd for cmd in calls)
    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT file_path FROM correction_history").fetchall()
    assert rows and Path(rows[0][0]).name == "sample.py"
