from pathlib import Path

from unified_database_management_system import UnifiedDatabaseManager


def test_verify_expected_databases(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(repo_root))
    manager = UnifiedDatabaseManager(workspace_root=str(repo_root))
    expected_ok, missing = manager.verify_expected_databases()
    assert expected_ok, f"Missing database files: {missing}"
