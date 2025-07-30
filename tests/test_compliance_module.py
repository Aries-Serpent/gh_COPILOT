import sqlite3
from pathlib import Path
from unittest.mock import patch

from enterprise_modules.compliance import validate_enterprise_operation, _log_rollback


def test_recursion_detection(tmp_path: Path) -> None:
    nested = tmp_path / tmp_path.name
    nested.mkdir()
    with patch.dict('os.environ', {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        assert not validate_enterprise_operation(str(tmp_path))


def test_log_rollback(tmp_path: Path) -> None:
    with patch.dict('os.environ', {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        _log_rollback("file.py", "file.py.bak")
        db = tmp_path / "databases" / "analytics.db"
        with sqlite3.connect(db) as conn:
            row = conn.execute(
                "SELECT target, backup FROM rollback_logs"
            ).fetchone()
        assert row == ("file.py", "file.py.bak")
