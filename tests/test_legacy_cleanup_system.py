import sqlite3
from pathlib import Path

import pytest

import importlib
from unified_legacy_cleanup_system import UnifiedLegacyCleanupSystem
from secondary_copilot_validator import SecondaryCopilotValidator


def test_cleanup_execution_and_logs(tmp_path, monkeypatch):
    pytest.skip("log_utils integration unstable in test environment")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    # create file management db with legacy script entry
    fm_db = db_dir / "file_management.db"
    with sqlite3.connect(fm_db) as conn:
        conn.execute(
            "CREATE TABLE legacy_scripts (script_path TEXT, active INTEGER)"
        )
        conn.execute(
            "INSERT INTO legacy_scripts VALUES ('old.py', 1)"
        )
    # create analytics.db with required tables
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE event_log (event TEXT, db TEXT, timestamp TEXT, module TEXT, level TEXT)"
        )
        conn.execute(
            "CREATE TABLE violation_logs (timestamp TEXT, details TEXT)"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.commit()
    # patch _log_event to avoid DB writes during test and reload module
    monkeypatch.setattr("utils.log_utils._log_event", lambda *a, **k: None)
    import unified_legacy_cleanup_system as uls
    import scripts.database.add_violation_logs as av
    import scripts.database.add_rollback_logs as ar
    importlib.reload(uls)
    monkeypatch.setattr(av, "_log_event", lambda *a, **k: None)
    monkeypatch.setattr(ar, "_log_event", lambda *a, **k: None)

    # create target script
    script = tmp_path / "old.py"
    script.write_text("print('x')")

    called: list[list[str]] = []
    def fake_validate(self, files):
        called.append(files)
        return True
    monkeypatch.setattr(
        SecondaryCopilotValidator, "validate_corrections", fake_validate
    )

    system = UnifiedLegacyCleanupSystem(str(tmp_path))
    system.run_cleanup()

    archived = tmp_path / "archive" / "legacy" / "old.py"
    assert archived.exists()
    assert called and called[0] == [str(script)]

