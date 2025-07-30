import sqlite3
from pathlib import Path

from session_management_consolidation_executor import EnterpriseUtility


def test_enterprise_utility_logs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "bk"))
    (tmp_path / "databases").mkdir()
    util = EnterpriseUtility(str(tmp_path))
    assert util.execute_utility()
    db = tmp_path / "databases" / "analytics.db"
    with sqlite3.connect(db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM event_log WHERE event='utility_start'"
        ).fetchone()[0]
    assert count == 1
