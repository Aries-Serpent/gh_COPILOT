#!/usr/bin/env python3

<<<<<<< HEAD

from scripts.database.database_purification_engine import DatabasePurificationEngine
=======
from database_purification_engine import DatabasePurificationEngine
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_engine_uses_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    engine = DatabasePurificationEngine()
    assert engine.workspace_path == tmp_path
