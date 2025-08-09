import scripts.wlc_session_manager as wsm


def test_log_action_invokes_record_and_logger(monkeypatch):
    calls = {"record": False, "logger": False}

    def fake_record(session_id, action, statement, ts):
        calls["record"] = True

    def fake_logger(action, statement, ts=None):
        calls["logger"] = True

    monkeypatch.setattr(wsm, "record_codex_action", fake_record)
    monkeypatch.setattr(wsm, "log_codex_logger_action", fake_logger)

    wsm.log_action("sess", "act", "stmt")

    assert calls["record"] and calls["logger"]
