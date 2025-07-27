from session_management_consolidation_executor import EnterpriseUtility
from utils.log_utils import _log_event


def test_log_event_simulation(tmp_path):
    db_path = tmp_path / "databases" / "analytics.db"
    db_path.parent.mkdir(parents=True)
    assert _log_event({"event": "unit_test"}, db_path=db_path)


def test_zero_byte_detection_logs(monkeypatch, tmp_path):
    events = []

    def fake_log(event, **kwargs):
        events.append(event)
        return True

    monkeypatch.setattr("session_management_consolidation_executor._log_event", fake_log)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup = tmp_path / "backup"
    backup.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup))

    (tmp_path / "empty.txt").touch()
    util = EnterpriseUtility(str(tmp_path))
    assert util.execute_utility() is False
    assert any(e.get("event") == "zero_byte_detected" for e in events)
