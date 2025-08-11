import sqlite3
from session_management_consolidation_executor import EnterpriseUtility
import utils.log_utils as log_utils


def test_session_triggers_backup(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    db_dir = workspace / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    sqlite3.connect(analytics_db).close()
    logs_dir = workspace / "logs"
    logs_dir.mkdir()
    (logs_dir / "run.log").write_text("log", encoding="utf-8")
    backup_root = tmp_path.parent / "backups"
    backup_root.mkdir()
    monkeypatch.setattr(log_utils, "_can_create_analytics_db", lambda db_path: True)
    orig_log_event = log_utils.log_event
    def _log_event(event, *, table=log_utils.DEFAULT_LOG_TABLE, db_path=analytics_db):
        orig_log_event(event, table=table, db_path=db_path)
    monkeypatch.setattr(log_utils, "log_event", _log_event)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    util = EnterpriseUtility(str(workspace))
    util.execute_utility()
    scheduled = list(backup_root.glob("scheduled_backup_*.bak"))
    assert scheduled
    with sqlite3.connect(analytics_db) as conn:
        rows = list(
            conn.execute(
                "SELECT description FROM event_log WHERE description='session_backup'"
            )
        )
    assert rows
