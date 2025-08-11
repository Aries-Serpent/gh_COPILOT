from __future__ import annotations

from quantum.framework import QuantumExecutor, SimulatorBackend
from quantum.providers import ibm as ibm_provider
from quantum.models import QuantumModel

try:  # pragma: no cover - optional demo model
    from quantum.models import DemoModel
except Exception:  # noqa: BLE001 - broad for optional import
    DemoModel = None
import pytest


def test_executor_falls_back_to_simulator(monkeypatch):
    monkeypatch.setattr(
        ibm_provider.IBMBackendProvider, "is_available", lambda self: False
    )
    executor = QuantumExecutor(provider="ibm")
    assert isinstance(executor.backend, SimulatorBackend)
    assert executor.use_hardware is False


class _DummyModel(QuantumModel):
    def build_circuit(self):
        return "test-circuit"


def test_model_run_uses_simulator(monkeypatch):
    monkeypatch.setattr(
        ibm_provider.IBMBackendProvider, "is_available", lambda self: False
    )
    monkeypatch.setenv("QUANTUM_PROVIDER", "ibm")
    model = _DummyModel()
    result = model.run()
    assert result == {"simulated": True, "circuit": "test-circuit"}


@pytest.mark.skipif(DemoModel is None, reason="DemoModel not available")
def test_demo_model(monkeypatch):
    """DemoModel should execute using the simulator backend."""

    monkeypatch.setattr(
        ibm_provider.IBMBackendProvider, "is_available", lambda self: False
    )
    monkeypatch.setenv("QUANTUM_PROVIDER", "ibm")
    model = DemoModel()
    result = model.run()
    assert result["simulated"] is True
