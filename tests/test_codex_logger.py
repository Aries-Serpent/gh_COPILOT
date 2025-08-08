import sqlite3
import subprocess
from pathlib import Path

from utils import codex_logger


def test_log_action_records_entry(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    # Reload module to pick up workspace path
    from importlib import reload
    reload(codex_logger)

    codex_logger.log_action("test", "hello world")
    db_file = tmp_path / "databases" / "codex_logs.db"
    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        row = conn.execute("SELECT action, statement FROM codex_logs").fetchone()
    assert row == ("test", "hello world")


def test_codex_logs_tracked_by_lfs():
    repo_root = Path(__file__).resolve().parents[1]
    db_path = repo_root / "databases" / "codex_logs.db"
    assert db_path.exists()
    result = subprocess.run(
        ["git", "lfs", "ls-files", str(db_path.relative_to(repo_root))],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_root,
    )
    assert "codex_logs.db" in result.stdout
