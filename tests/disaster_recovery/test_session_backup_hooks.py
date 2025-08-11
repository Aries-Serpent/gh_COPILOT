import sqlite3

from session_management_consolidation_executor import EnterpriseUtility
import session_management_consolidation_executor as smce
import unified_disaster_recovery_system as uds
from types import SimpleNamespace
from contextlib import contextmanager


def test_session_backup_creates_file_and_log(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    (workspace / "databases").mkdir(parents=True)
    db_path = workspace / "databases" / "analytics.db"
    sqlite3.connect(db_path).close()
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.setenv("ANALYTICS_DB", str(db_path))
    @contextmanager
    def _noop(*a, **k):
        yield
    monkeypatch.setattr(smce, "ensure_no_zero_byte_files", _noop)
    monkeypatch.setattr(smce, "finalize_session", lambda *a, **k: None)
    monkeypatch.setattr(EnterpriseUtility, "_validate_environment", lambda self: True)
    monkeypatch.setattr(
        smce.SessionProtocolValidator,
        "validate_startup",
        lambda self: SimpleNamespace(is_success=True),
    )
    monkeypatch.setattr(EnterpriseUtility, "perform_utility_function", lambda self: True)

    events = []
    monkeypatch.setattr(uds.enterprise_logging, "log_event", lambda e, **k: events.append(e))

    util = EnterpriseUtility(workspace)
    util.execute_utility()

    backups = list(backup_root.glob("scheduled_backup_*.bak"))
    assert backups
    assert any(evt.get("description") == "session_backup" for evt in events)
