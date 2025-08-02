# [Test]: WLC Session Manager CLI Tests
# > Generated: 2025-07-24 06:42 | Author: mbaetiong

import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wlc_session_manager.py"
DEFAULT_DB = Path("databases/production.db")


def copy_db_to_tmp(tmp_path):
    temp_db = tmp_path / "production.db"
    shutil.copy(DEFAULT_DB, temp_db)
    return temp_db


def test_cli_execution(tmp_path):
    temp_db = copy_db_to_tmp(tmp_path)
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    env["TEST_MODE"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    env["TEST_MODE"] = "1"
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
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    with sqlite3.connect(temp_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    assert count == before


def test_cli_orchestrate(tmp_path):
    temp_db = copy_db_to_tmp(tmp_path)
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    env["TEST_MODE"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    env["TEST_MODE"] = "1"

    result = subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--steps",
            "1",
            "--db-path",
            str(temp_db),
            "--orchestrate",
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_cli_invalid_env(tmp_path):
    temp_db = copy_db_to_tmp(tmp_path)
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["PYTHONPATH"] = str(Path.cwd())
    env.pop("GH_COPILOT_BACKUP_ROOT", None)
    env.pop("TEST_MODE", None)
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
    err = result.stderr.lower()
    assert "environment variables" in err or "backup root" in err
