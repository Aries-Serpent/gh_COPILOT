"""Tests for the pid_recursion_guard decorator."""

# flake8: noqa

import os
import sqlite3
import sys
import types
from pathlib import Path

import pytest

sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=lambda x, **_: x))
class _DummyPathManager:
    @staticmethod
    def get_workspace_path():
        return Path.cwd()

    @staticmethod
    def get_backup_root():
        return Path("/tmp")

sys.modules.setdefault(
    "utils.cross_platform_paths",
    types.SimpleNamespace(CrossPlatformPathManager=_DummyPathManager),
)
sys.modules.setdefault(
    "utils.log_utils", types.SimpleNamespace(send_dashboard_alert=lambda *a, **k: None)
)
_scripts = types.ModuleType("scripts")
_database = types.ModuleType("scripts.database")
def _ensure_violation_logs(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS violation_logs (timestamp TEXT, details TEXT)"
        )
        conn.commit()

_database.add_violation_logs = types.SimpleNamespace(
    ensure_violation_logs=_ensure_violation_logs
)
_database.add_rollback_logs = types.SimpleNamespace(
    ensure_rollback_logs=lambda *a, **k: None
)
_scripts.database = _database
_scripts.run_migrations = types.SimpleNamespace(
    ensure_migrations_applied=lambda *a, **k: None
)
sys.modules.setdefault("scripts", _scripts)
sys.modules.setdefault("scripts.database", _database)
sys.modules.setdefault(
    "scripts.database.add_violation_logs", _database.add_violation_logs
)
sys.modules.setdefault(
    "scripts.database.add_rollback_logs", _database.add_rollback_logs
)
sys.modules.setdefault("scripts.run_migrations", _scripts.run_migrations)

from enterprise_modules.compliance import (
    MAX_RECURSION_DEPTH,
    ComplianceError,
    pid_recursion_guard,
)


@pid_recursion_guard
def _recursive_call(level: int) -> str:
    if level > 0:
        return _recursive_call(level - 1)
    return "done"


def test_pid_recursion_guard_logs_violation(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    # Within threshold executes successfully
    assert _recursive_call(MAX_RECURSION_DEPTH - 1) == "done"

    # Exceeding threshold raises and logs a violation with PID details
    with pytest.raises(ComplianceError):
        _recursive_call(MAX_RECURSION_DEPTH)

    db = tmp_path / "databases" / "analytics.db"
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT details FROM violation_logs").fetchall()
    assert any(f"pid={os.getpid()}" in r[0] for r in rows)


def test_pid_recursion_guard_records_depth(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    _recursive_call(MAX_RECURSION_DEPTH - 1)
    with pytest.raises(ComplianceError):
        _recursive_call(MAX_RECURSION_DEPTH)

    db = tmp_path / "databases" / "analytics.db"
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT details FROM violation_logs").fetchall()
    assert any(f"depth={MAX_RECURSION_DEPTH + 1}" in r[0] for r in rows)

