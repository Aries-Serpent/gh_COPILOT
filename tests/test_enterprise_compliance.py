from utils import log_utils


def test_compliance_logging_and_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from session_management_consolidation_executor import EnterpriseUtility

    events = []

    def fake_log(event, **kwargs):
        events.append(event.get("event"))
        return True

    monkeypatch.setattr(log_utils, "_log_event", fake_log)
    monkeypatch.setattr(
        "session_management_consolidation_executor._log_event",
        fake_log,
    )

    util = EnterpriseUtility(str(tmp_path))
    assert util.execute_utility() is True
    assert "utility_start" in events
    assert "utility_success" in events

    events.clear()
    (tmp_path / "bad.txt").write_text("")
    util = EnterpriseUtility(str(tmp_path))
    assert util.execute_utility() is False
    assert "utility_failed" in events
