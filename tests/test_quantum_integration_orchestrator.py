from scripts.automation import quantum_integration_orchestrator as qio


class DummyValidator:
    def __init__(self):
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


class DummyUtility:
    def execute_utility(self):
        return True


def test_validator_called(monkeypatch):
    dummy_validator = DummyValidator()
    monkeypatch.setattr(qio, "SecondaryCopilotValidator", lambda: dummy_validator)
    monkeypatch.setattr(qio, "EnterpriseUtility", lambda: DummyUtility())
    assert qio.main() is True
    assert dummy_validator.called
