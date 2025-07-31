import os
import sqlite3
from pathlib import Path

import pytest

from unified_legacy_cleanup_system import UnifiedLegacyCleanupSystem


@pytest.fixture()
def setup_workspace(tmp_path: Path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    db_dir = workspace / "databases"
    db_dir.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backup"))
    # create minimal analytics.db for logging tests
    with sqlite3.connect(db_dir / "analytics.db") as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS event_log ("
            "id INTEGER PRIMARY KEY, event TEXT, module TEXT, level TEXT, timestamp TEXT)"
        )
    return workspace


def test_cleanup_removes_files_and_logs(setup_workspace: Path, monkeypatch):
    deprecated = setup_workspace / "old_deprecated.py"
    deprecated.write_text("print('legacy')\n")
    events = []
    monkeypatch.setattr(
        "unified_legacy_cleanup_system._log_event",
        lambda evt, **_: events.append(evt),
    )
    system = UnifiedLegacyCleanupSystem(str(setup_workspace))
    assert system.run_cleanup()
    assert not deprecated.exists()
    backup_file = Path(os.environ["GH_COPILOT_BACKUP_ROOT"]) / "legacy_cleanup" / deprecated.name
    assert backup_file.exists()
    assert any(e.get("event") == "removed_file" for e in events)


def test_cleanup_rollback_on_error(setup_workspace: Path, monkeypatch):
    bad_file = setup_workspace / "remove_deprecated.py"
    bad_file.write_text("print('x')\n")
    called = {}

    def fake_remove(_):
        raise OSError("fail")

    def fake_recover():
        called["recover"] = True

    monkeypatch.setattr(Path, "unlink", fake_remove)
    monkeypatch.setattr(
        "unified_legacy_cleanup_system.UnifiedDisasterRecoverySystem.perform_recovery",
        lambda self: fake_recover(),
    )
    monkeypatch.setattr(
        "unified_legacy_cleanup_system._log_event",
        lambda *_, **__: None,
    )
    system = UnifiedLegacyCleanupSystem(str(setup_workspace))
    assert not system.run_cleanup()
    assert called.get("recover")


def test_cleanup_writes_to_db(setup_workspace: Path, monkeypatch):
    analytics = setup_workspace / "databases" / "analytics.db"
    system = UnifiedLegacyCleanupSystem(str(setup_workspace))
    (setup_workspace / "temp_deprecated.py").write_text("pass\n")

    def fake_log(event, *, db_path, **_):
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO event_log (event) VALUES (?)", (event["event"],))
            conn.commit()

    monkeypatch.setattr("unified_legacy_cleanup_system._log_event", fake_log)

    assert system.run_cleanup()
    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT event FROM event_log").fetchall()
    assert rows
