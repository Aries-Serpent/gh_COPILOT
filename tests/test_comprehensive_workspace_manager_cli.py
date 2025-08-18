"""Tests for COMPREHENSIVE_WORKSPACE_MANAGER CLI."""

from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(reason="workspace manager CLI under investigation")

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "session" / "COMPREHENSIVE_WORKSPACE_MANAGER.py"
DEFAULT_DB = Path("databases/production.db")


def copy_db_to_tmp(tmp_path: Path) -> Path:
    temp_db = tmp_path / "production.db"
    shutil.copy(DEFAULT_DB, temp_db)
    return temp_db


def test_cli_start_end(tmp_path):
    temp_db = copy_db_to_tmp(tmp_path)
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path.parent / "backups")
    env["PYTHONPATH"] = str(Path.cwd())

    result = subprocess.run(
        ["python", str(SCRIPT), "--SessionStart", "--db-path", str(temp_db), "-AutoFix"],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0

    result = subprocess.run(
        ["python", str(SCRIPT), "--SessionEnd", "--db-path", str(temp_db)],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0

    with sqlite3.connect(temp_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM session_wrapups").fetchone()[0]
    assert count >= 1


def test_cli_missing_env(tmp_path):
    temp_db = copy_db_to_tmp(tmp_path)
    env = os.environ.copy()
    env.pop("GH_COPILOT_BACKUP_ROOT", None)
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["PYTHONPATH"] = str(Path.cwd())

    result = subprocess.run(
        ["python", str(SCRIPT), "--SessionStart", "--db-path", str(temp_db)],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
