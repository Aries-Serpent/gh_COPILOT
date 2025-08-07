#!/usr/bin/env python3

from session_management_consolidation_executor import EnterpriseUtility
import sqlite3
import unified_session_management_system as usm


def test_consolidation_executor_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    backup_root = tmp_path.parent / "backups"
    backup_root.mkdir(exist_ok=True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.chdir(tmp_path)
    db_file = tmp_path / "databases" / "analytics.db"
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    util = EnterpriseUtility(str(tmp_path))
    assert util.perform_utility_function() is True
    assert util.execute_utility() is True


def test_consolidation_executor_fails_on_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    backup_root = tmp_path.parent / "backups"
    backup_root.mkdir(exist_ok=True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.chdir(tmp_path)
    db_file = tmp_path / "databases" / "analytics.db"
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    (tmp_path / "empty.txt").write_text("")
    util = EnterpriseUtility(str(tmp_path))
    assert util.perform_utility_function() is False
    with sqlite3.connect(db_file) as conn:
        paths = conn.execute("SELECT path, phase FROM zero_byte_files").fetchall()
        events = conn.execute(
            "SELECT description FROM event_log WHERE description='zero_byte_detected'"
        ).fetchall()
    assert paths and paths[0][0].endswith("empty.txt") and paths[0][1] == "before"
    assert events


def test_consolidation_executor_fails_on_subdir_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    backup_root = tmp_path.parent / "backups"
    backup_root.mkdir(exist_ok=True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.chdir(tmp_path)
    db_file = tmp_path / "databases" / "analytics.db"
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "empty.txt").write_text("")
    util = EnterpriseUtility(str(tmp_path))
    assert util.perform_utility_function() is False
