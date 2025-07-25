import sqlite3
from pathlib import Path

from scripts.unified_legacy_cleanup_system import (
    UnifiedLegacyCleanupSystem,
    main,
)


def setup_db(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    file_db = db_dir / "file_management.db"
    with sqlite3.connect(file_db) as conn:
        conn.execute(
            "CREATE TABLE legacy_scripts (script_path TEXT, active INTEGER)"
        )
        conn.execute(
            "INSERT INTO legacy_scripts VALUES ('demo.py', 1)"
        )


def test_run_cleanup(tmp_path: Path):
    setup_db(tmp_path)
    (tmp_path / "demo.py").write_text("print('hi')\n")
    system = UnifiedLegacyCleanupSystem(workspace_path=tmp_path)
    system.run_cleanup(dry_run=False)
    archived = tmp_path / "archive" / "legacy" / "demo.py"
    assert archived.exists()


def test_cli_dry_run(tmp_path: Path, monkeypatch):
    setup_db(tmp_path)
    (tmp_path / "demo.py").write_text("print('hi')\n")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    assert main(["--dry-run"]) == 0
