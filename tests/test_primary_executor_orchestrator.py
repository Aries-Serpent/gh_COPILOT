import types

from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator


def test_orchestrator_invokes_executor_and_validator(monkeypatch):
    calls = {"exec": False, "validate": False}

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

    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.PrimaryCopilotExecutor",
        DummyExecutor,
    )
    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.SecondaryCopilotValidator",
        DummyValidator,
    )

    orch = DualCopilotOrchestrator()
    success, validated = orch.run(lambda: True, ["a.py"], timeout_minutes=1)

    assert success
    assert validated
    assert calls["exec"]
    assert calls["validate"]

