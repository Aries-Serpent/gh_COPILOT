import types

from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator


def test_orchestrator_invokes_executor_and_validator(monkeypatch):
    calls = {"exec": False, "validate": False, "logged": False}

    class DummyExecutor:
        def __init__(self, task_name: str, timeout_minutes: int = 30, logger=None) -> None:
            pass

        def execute_with_monitoring(self, phases, operation):
            calls["exec"] = True
            return types.SimpleNamespace(), operation()

    class DummyValidator:
        def __init__(self, logger=None):
            pass

        def validate_corrections(self, files):
            calls["validate"] = True
            return True

    class DummyMonitor:
        def execute_utility(self):
            return True

    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.PrimaryCopilotExecutor",
        DummyExecutor,
    )
    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.SecondaryCopilotValidator",
        DummyValidator,
    )
    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.EnterpriseUtility",
        DummyMonitor,
    )
    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.collect_metrics",
        lambda: {"session_id": "s1"},
    )

    def fake_log(event, **_):
        calls["logged"] = True
        assert event["event"] == "dual_copilot_run"

    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator._log_event",
        fake_log,
    )

    orch = DualCopilotOrchestrator()
    success, validated, metrics = orch.run(lambda: True, ["a.py"], timeout_minutes=1)

    assert success
    assert validated
    assert metrics["session_id"] == "s1"
    assert calls["exec"]
    assert calls["validate"]
    assert calls["logged"]
