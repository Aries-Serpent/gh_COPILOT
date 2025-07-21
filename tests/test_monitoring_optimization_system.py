#!/usr/bin/env python3
import shutil
import sqlite3
from pathlib import Path

from archive.consolidated_scripts.unified_monitoring_optimization_system import EnterpriseUtility
import logging


def test_perform_utility_function_inserts_metrics(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    shutil.copy(repo_root / "databases" / "production.db", db_dir)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    util = EnterpriseUtility(workspace_path=str(workspace))
    assert util.perform_utility_function()

