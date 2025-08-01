import numpy as np
import pytest

from quantum.optimizers import quantum_optimizer as qo
from quantum.optimizers.quantum_optimizer import QuantumOptimizer


def objective(x: np.ndarray) -> float:
    return float(np.sum(x**2))


class MockBackend:
    def run(self, circ):  # pragma: no cover - interface only
        class Result:
            def result(self):
                return None

        return Result()


class MockProvider:
    def __init__(self, *_, **__):
        pass

    def get_backend(self, name):  # pragma: no cover - simple mock
        return MockBackend()


@pytest.mark.skipif(not qo.QISKIT_AVAILABLE, reason="Qiskit not available")
def test_configure_backend_hardware(monkeypatch):
    monkeypatch.setattr(qo, "IBMProvider", lambda token=None: MockProvider())
    opt = QuantumOptimizer(objective, [(-1, 1)], method="simulated_annealing")
    backend = opt.configure_backend("mock_backend", use_hardware=True)
    assert backend is opt.backend
    assert opt.use_hardware


@pytest.mark.skipif(not qo.QISKIT_AVAILABLE, reason="Qiskit not available")
def test_configure_backend_fallback(monkeypatch):
    def bad_provider(*_, **__):
        raise RuntimeError("bad credentials")

    monkeypatch.setattr(qo, "IBMProvider", bad_provider)
    opt = QuantumOptimizer(objective, [(-1, 1)], method="simulated_annealing")
    backend = opt.configure_backend("mock_backend", use_hardware=True)
    assert backend is opt.backend
    assert opt.use_hardware is False
