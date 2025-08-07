from __future__ import annotations

from quantum.framework import QuantumExecutor, SimulatorBackend, backend as fw_backend
from quantum.models import QuantumModel


def test_executor_falls_back_to_simulator(monkeypatch):
    monkeypatch.setattr(fw_backend, "init_ibm_backend", lambda token=None: (None, False))
    executor = QuantumExecutor()
    assert isinstance(executor.backend, SimulatorBackend)
    assert executor.use_hardware is False


class _DummyModel(QuantumModel):
    def build_circuit(self):
        return "test-circuit"


def test_model_run_uses_simulator(monkeypatch):
    monkeypatch.setattr(fw_backend, "init_ibm_backend", lambda token=None: (None, False))
    model = _DummyModel()
    result = model.run()
    assert result == {"simulated": True, "circuit": "test-circuit"}
