import numpy as np
import pytest

from ghc_quantum.optimizers import quantum_optimizer as qo
from ghc_quantum.optimizers.quantum_optimizer import QuantumOptimizer


def objective(x: np.ndarray) -> float:
    return float(np.sum(x**2))


class MockBackend:
    def run(self, circ):  # pragma: no cover - interface only
        class Result:
            def result(self):
                return None

        return Result()


class MockHardwareBackend(MockBackend):
    name = "hardware"

    class _Cfg:
        simulator = False

    def configuration(self):
        return self._Cfg()


class MockSimulatorBackend(MockBackend):
    name = "simulator"

    class _Cfg:
        simulator = True

    def configuration(self):
        return self._Cfg()


class MockProvider:
    def __init__(self, *_, **__):
        pass

    def get_backend(self, name):  # pragma: no cover - simple mock
        return MockBackend()


@pytest.mark.skipif(not qo.QISKIT_AVAILABLE, reason="Qiskit not available")
def test_configure_backend_hardware(monkeypatch):
    monkeypatch.setattr(
        qo, "get_backend", lambda name, use_hardware: MockHardwareBackend()
    )
    opt = QuantumOptimizer(objective, [(-1, 1)], method="simulated_annealing")
    backend = opt.configure_backend("mock_backend", use_hardware=True)
    assert isinstance(backend, MockHardwareBackend)
    assert opt.use_hardware


@pytest.mark.skipif(not qo.QISKIT_AVAILABLE, reason="Qiskit not available")
def test_configure_backend_fallback(monkeypatch):
    def bad_provider(*_, **__):
        raise RuntimeError("bad credentials")

    monkeypatch.setattr(
        qo, "get_backend", lambda name, use_hardware: MockSimulatorBackend()
    )
    opt = QuantumOptimizer(objective, [(-1, 1)], method="simulated_annealing")
    backend = opt.configure_backend("mock_backend", use_hardware=True)
    assert isinstance(backend, MockSimulatorBackend)
    assert opt.use_hardware is False
