from datetime import datetime

import scripts.orchestrators.unified_wrapup_orchestrator as uwo


def test_main_triggers_wlc(monkeypatch):
    called = {}

    def fake_run_session(*args, **kwargs):
        called["yes"] = True

    monkeypatch.setattr(uwo, "run_session", fake_run_session)
    monkeypatch.setenv("TEST_MODE", "1")

    def fake_execute(self):
        return uwo.WrapUpResult(session_id="id", start_time=datetime.now(), status="COMPLETED")

    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "execute_unified_wrapup", fake_execute)

    exit_code = uwo.main()
    assert exit_code == 0
    assert called.get("yes")
