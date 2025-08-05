"""Tests for anti-recursion guard PID logging and depth enforcement."""

from __future__ import annotations

import sqlite3
import threading
import types
import sys
from pathlib import Path
import time

sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=lambda x, **_: x))


class _DummyPathManager:
    @staticmethod
    def get_workspace_path() -> Path:  # pragma: no cover - simple stub
        return Path.cwd()

    @staticmethod
    def get_backup_root() -> Path:  # pragma: no cover - simple stub
        return Path("/tmp")


sys.modules.setdefault(
    "utils.cross_platform_paths", types.SimpleNamespace(CrossPlatformPathManager=_DummyPathManager)
)
sys.modules.setdefault(
    "utils.log_utils", types.SimpleNamespace(send_dashboard_alert=lambda *a, **k: None)
)

_scripts = types.ModuleType("scripts")
_database = types.ModuleType("scripts.database")
_database.add_violation_logs = types.SimpleNamespace(ensure_violation_logs=lambda *a, **k: None)
_database.add_rollback_logs = types.SimpleNamespace(ensure_rollback_logs=lambda *a, **k: None)
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
    anti_recursion_guard,
)


def _count_entries(db_path: Path, pattern: str) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM recursion_pid_log WHERE path LIKE ?", (pattern,)
        )
        return cur.fetchone()[0]


def test_pid_entry_logging(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    @anti_recursion_guard
    def dummy():
        return 42

    assert dummy() == 42
    assert dummy() == 42

    db = tmp_path / "databases" / "analytics.db"
    assert _count_entries(db, "%/entry") == 2
    assert _count_entries(db, "%/exit") == 2


def test_depth_overflow(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    @anti_recursion_guard
    def guarded():
        time.sleep(0.2)

    errors: list[RuntimeError] = []
    barrier = threading.Barrier(MAX_RECURSION_DEPTH + 1)

    def target():
        try:
            barrier.wait()
            guarded()
        except RuntimeError as exc:  # pragma: no cover - depends on timing
            errors.append(exc)

    threads = [threading.Thread(target=target) for _ in range(MAX_RECURSION_DEPTH + 1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert any("Recursion depth exceeded" in str(e) for e in errors)

