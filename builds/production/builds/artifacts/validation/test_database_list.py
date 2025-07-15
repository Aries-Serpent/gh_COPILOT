#!/usr/bin/env python3
from pathlib import Path

from unified_database_management_system import UnifiedDatabaseManager
import logging


def test_verify_expected_databases(monkeypatch) -> None:
    """Validate expected databases exist using repository root."""
    # ``parents[5]`` ascends from ``validation/`` to the repository root.
    repo_root = Path(__file__).resolve().parents[5]
    monkeypatch.setenv(UnifiedDatabaseManager.WORKSPACE_ENV_VAR, str(repo_root))
    manager = UnifiedDatabaseManager()
    expected_ok, missing = manager.verify_expected_databases()
    assert expected_ok, f"Missing database files: {missing}"
