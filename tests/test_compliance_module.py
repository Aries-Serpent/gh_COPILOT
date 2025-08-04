import os
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from enterprise_modules.compliance import (
    validate_enterprise_operation,
    _log_rollback,
    _detect_recursion,
    validate_environment,
    enforce_anti_recursion,
    ComplianceError,
    MAX_RECURSION_DEPTH,
)


def test_recursion_detection(tmp_path: Path) -> None:
    nested = tmp_path / tmp_path.name
    nested.mkdir()
    with patch.dict("os.environ", {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        assert not validate_enterprise_operation(str(tmp_path))
        db = tmp_path / "databases" / "analytics.db"
        with sqlite3.connect(db) as conn:
            details = conn.execute("SELECT details FROM violation_logs").fetchall()
        assert any("recursive_" in d[0] for d in details)


def test_dashboard_alert_on_recursion(tmp_path: Path) -> None:
    nested = tmp_path / tmp_path.name
    nested.mkdir()
    with patch.dict("os.environ", {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        with patch("enterprise_modules.compliance.send_dashboard_alert") as alert:
            validate_enterprise_operation(str(tmp_path))
            assert alert.call_count >= 1


def test_recursion_symlink(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}_outside"
    outside.mkdir()
    link = tmp_path / tmp_path.name
    link.symlink_to(outside, target_is_directory=True)

    assert not _detect_recursion(tmp_path)


def test_log_rollback(tmp_path: Path) -> None:
    with patch.dict("os.environ", {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        _log_rollback("file.py", "file.py.bak")
        db = tmp_path / "databases" / "analytics.db"
        with sqlite3.connect(db) as conn:
            row = conn.execute("SELECT target, backup FROM rollback_logs").fetchone()
        assert row == ("file.py", "file.py.bak")


def test_detect_recursion_true(tmp_path: Path) -> None:
    """``_detect_recursion`` should return True when a nested folder matches."""
    nested = tmp_path / tmp_path.name
    nested.mkdir()
    assert _detect_recursion(tmp_path)


def test_detect_recursion_false(tmp_path: Path) -> None:
    """``_detect_recursion`` should return False without matching folders."""
    assert not _detect_recursion(tmp_path)


def test_validate_environment(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    with pytest.raises(ComplianceError):
        validate_environment()
    (tmp_path / "production.db").touch()
    assert validate_environment() is True


def test_enforce_anti_recursion() -> None:
    enforce_anti_recursion(SimpleNamespace(recursion_depth=1))
    with pytest.raises(ComplianceError):
        enforce_anti_recursion(SimpleNamespace(recursion_depth=10))


def test_enforce_anti_recursion_nested_limit() -> None:
    ctx = SimpleNamespace()
    for _ in range(MAX_RECURSION_DEPTH):
        assert enforce_anti_recursion(ctx) is True
        assert ctx.parent_pid == os.getppid()
        assert ctx.pid == os.getpid()

    with pytest.raises(ComplianceError):
        enforce_anti_recursion(ctx)


def test_enforce_anti_recursion_pid_mismatch() -> None:
    ctx = SimpleNamespace(recursion_depth=0, pid=-1)
    with pytest.raises(ComplianceError):
        enforce_anti_recursion(ctx)


def test_detect_recursion_depth_abort(tmp_path: Path) -> None:
    current = tmp_path
    for i in range(MAX_RECURSION_DEPTH + 1):
        current = current / f"d{i}"
        current.mkdir()
    assert _detect_recursion(tmp_path)
    assert getattr(_detect_recursion, "aborted") is True
    assert (
        getattr(_detect_recursion, "max_depth_reached") >= MAX_RECURSION_DEPTH + 1
    )


def test_detect_recursion_pid_record(tmp_path: Path) -> None:
    _detect_recursion(tmp_path)
    assert getattr(_detect_recursion, "last_pid") == os.getpid()


def test_validate_operation_depth_logs(tmp_path: Path) -> None:
    current = tmp_path
    for i in range(MAX_RECURSION_DEPTH + 1):
        current = current / f"d{i}"
        current.mkdir()
    with patch.dict("os.environ", {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        assert not validate_enterprise_operation(str(tmp_path))
        db = tmp_path / "databases" / "analytics.db"
        with sqlite3.connect(db) as conn:
            details = {
                row[0]
                for row in conn.execute("SELECT details FROM violation_logs")
            }
        assert "recursive_workspace" in details or "recursive_target" in details
