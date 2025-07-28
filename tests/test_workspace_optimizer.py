import os
import sqlite3
import shutil
from pathlib import Path

from scripts.file_management.workspace_optimizer import WorkspaceOptimizer, main


def setup_db(db_path: Path, file_rel: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO tracked_scripts (script_name, script_path, last_modified) VALUES (?, ?, ?)",
            (Path(file_rel).name, file_rel, "2000-01-01 00:00:00"),
        )


def test_optimizer_archives_and_logs(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    db_dir = workspace / "databases"
    archive_root = tmp_path / "backups"
    workspace.mkdir()
    db_dir.mkdir()
    shutil.copy(Path("databases/production.db"), db_dir / "production.db")
    test_file = workspace / "old.py"
    test_file.write_text("print('x')\n")
    setup_db(db_dir / "production.db", "/old.py")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(archive_root))

    optimizer = WorkspaceOptimizer(db_dir / "production.db")
    optimizer.optimize(workspace)

    assert not test_file.exists()
    archive = archive_root / "workspace_archive" / "old.py.gz"
    assert archive.exists()

    with sqlite3.connect(db_dir / "production.db") as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM workspace_optimization_metrics"
        ).fetchone()[0]
        assert count == 1


def test_cli_invokes_dual(monkeypatch, tmp_path):
    workspace = tmp_path / "ws"
    db_dir = workspace / "databases"
    workspace.mkdir()
    db_dir.mkdir()
    shutil.copy(Path("databases/production.db"), db_dir / "production.db")
    setup_db(db_dir / "production.db", "/dummy.py")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    called = {"run": False}

    class DummyOrchestrator:
        def __init__(self, logger=None):
            pass

        def run(self, primary, targets):
            called["run"] = True
            primary()
            return True

    monkeypatch.setattr(
        "scripts.file_management.workspace_optimizer.DualCopilotOrchestrator",
        DummyOrchestrator,
    )

    monkeypatch.chdir(workspace)
    assert main([]) == 0
    assert called["run"]
