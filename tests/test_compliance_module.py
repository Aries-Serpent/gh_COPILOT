import sqlite3
from pathlib import Path
from unittest.mock import patch

from enterprise_modules.compliance import (
    validate_enterprise_operation,
    _log_rollback,
    _detect_recursion,
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
