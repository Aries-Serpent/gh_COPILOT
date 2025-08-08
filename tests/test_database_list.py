#!/usr/bin/env python3
from pathlib import Path

<<<<<<< HEAD
from scripts.database.unified_database_management_system import UnifiedDatabaseManager
=======
from unified_database_management_system import UnifiedDatabaseManager
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_verify_expected_databases(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv(UnifiedDatabaseManager.WORKSPACE_ENV_VAR, str(repo_root))
    manager = UnifiedDatabaseManager()
    expected_ok, missing = manager.verify_expected_databases()
    assert expected_ok, f"Missing database files: {missing}"
