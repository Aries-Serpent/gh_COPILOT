#!/usr/bin/env python3
from session_management_consolidation_executor import EnterpriseUtility
from simplified_quantum_integration_orchestrator import hello_world
import unified_session_management_system as usm


def test_perform_utility_function_runs(tmp_path, monkeypatch):
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


def test_hello_world_output(capsys):
    hello_world()
    captured = capsys.readouterr()
    assert "Hello, world!" in captured.out
