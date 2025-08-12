from scripts.automation import quantum_integration_orchestrator as qio
import pytest
from unittest.mock import MagicMock


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
    monkeypatch.setattr(qio, "EnterpriseUtility", lambda *a, **k: DummyUtility())
    assert qio.main() is True
    assert dummy_validator.called


@pytest.mark.hardware
def test_backend_initialization(monkeypatch):
    backend = object()
    provider_mock = MagicMock()
    provider_mock.return_value.get_backend.return_value = backend
    monkeypatch.setattr("ghc_quantum.ibm_backend.IBMProvider", provider_mock)
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    util = qio.EnterpriseUtility(use_hardware=True)
    assert util.use_hardware
    assert util.backend is backend
