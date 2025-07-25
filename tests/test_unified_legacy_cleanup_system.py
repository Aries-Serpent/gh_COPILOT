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
        conn.execute("CREATE TABLE legacy_scripts (script_path TEXT, active INTEGER)")
        conn.execute("INSERT INTO legacy_scripts VALUES ('demo.py', 1)")


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


def test_logging(tmp_path: Path, monkeypatch):
    setup_db(tmp_path)
    (tmp_path / "demo.py").write_text("print('hi')\n")
    events = []

    def fake_log(event, **_):
        events.append(event)
        return True

    monkeypatch.setattr("scripts.unified_legacy_cleanup_system._log_event", fake_log)
    system = UnifiedLegacyCleanupSystem(workspace_path=tmp_path)
    system.run_cleanup(dry_run=False)
    assert any(e.get("event") == "legacy_cleanup_start" for e in events)
    assert any(e.get("event") == "archive_success" for e in events)
