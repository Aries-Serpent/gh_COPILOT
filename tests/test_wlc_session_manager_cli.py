import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

import scripts.wlc_session_manager as wsm


class DummyValidator:
    def __init__(self, logger=None):
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


def test_invalid_env(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    with pytest.raises(EnvironmentError):
        wsm.main()


def test_cli_execution(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("WLC_DB_PATH", str(temp_db))
    dummy = DummyValidator()
    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: dummy)
    monkeypatch.setenv("PYTHONPATH", str(Path(wsm.__file__).resolve().parent.parent))
    with sqlite3.connect(temp_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    result = subprocess.run(
        ["python", str(Path(wsm.__file__).resolve()), "--steps", "2"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM unified_wrapup_sessions")
        after = cur.fetchone()[0]
    assert after == before + 1
    log_files = list((backup_root / "logs").glob("wlc_*.log"))
    assert log_files
