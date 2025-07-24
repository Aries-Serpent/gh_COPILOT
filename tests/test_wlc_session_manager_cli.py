import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wlc_session_manager.py"


def test_cli_execution(tmp_path):
    temp_db = tmp_path / "production.db"
    shutil.copy(Path("databases/production.db"), temp_db)
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    env["PYTHONPATH"] = str(Path.cwd())
    with sqlite3.connect(temp_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]

    result = subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--steps",
            "1",
            "--db-path",
            str(temp_db),
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    with sqlite3.connect(temp_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    assert count == before + 1


def test_cli_invalid_env(tmp_path):
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["PYTHONPATH"] = str(Path.cwd())
    env.pop("GH_COPILOT_BACKUP_ROOT", None)
    temp_db = tmp_path / "production.db"
    shutil.copy(Path("databases/production.db"), temp_db)
    # Missing GH_COPILOT_BACKUP_ROOT
    result = subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--db-path",
            str(temp_db),
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "environment variables" in result.stderr
