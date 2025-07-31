import sqlite3
from pathlib import Path
import subprocess
from scripts.database.database_first_correction_engine import DatabaseFirstCorrectionEngine


def _setup_db(db_path: Path) -> None:
    sql = Path("databases/migrations/add_correction_history.sql").read_text()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS event_log (event TEXT, fix_count INTEGER)"
        )


def _create_workspace(tmp_path):
    (tmp_path / "production.db").touch()
    analytics = tmp_path / "analytics.db"
    _setup_db(analytics)
    sample = tmp_path / "sample.py"
    sample.write_text("print('hi')  \n", encoding="utf-8")
    return sample, analytics


def test_engine_applies_ruff_and_records_history(tmp_path, monkeypatch):
    sample, analytics = _create_workspace(tmp_path)
    engine = DatabaseFirstCorrectionEngine(workspace_path=str(tmp_path))
    engine.analytics_db = analytics

    calls = []

    def fake_run(cmd, *a, **kw):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = ""

        if cmd[:3] == ["ruff", "check", "--fix"]:
            R.stdout = "Found 2 errors (2 fixed, 0 remaining)."

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    engine.execute_database_driven_corrections()

    assert any(cmd[:2] == ["ruff", "--fix"] for cmd in calls)
    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT file_path FROM correction_history").fetchall()
        events = conn.execute("SELECT event, fix_count FROM event_log").fetchall()
    assert rows and Path(rows[0][0]).name == "sample.py"
    assert any(e[0] == "ruff_workspace_fix" and e[1] == 2 for e in events)


def test_cross_validation_success(tmp_path, monkeypatch):
    sample, analytics = _create_workspace(tmp_path)
    engine = DatabaseFirstCorrectionEngine(workspace_path=str(tmp_path))
    engine.analytics_db = analytics

    called = []
    monkeypatch.setattr(engine, "_run_ruff_fix", lambda f: called.append("fix"))
    monkeypatch.setattr(engine, "cross_validate_with_ruff", lambda f: called.append("check") or True)

    engine.execute_database_driven_corrections()

    assert "fix" in called and "check" in called
