import numpy as np
import pytest

from quantum.optimizers.quantum_optimizer import QuantumOptimizer

pytestmark = pytest.mark.timeout(60)


def test_simulated_annealing_runs():
    def obj(x):
        return np.sum((x - 1) ** 2)

    optimizer = QuantumOptimizer(obj, [(-2, 2), (-2, 2)], method="simulated_annealing")
    result = optimizer.run(x0=np.array([0.0, 0.0]), max_iter=10)
    assert "best_result" in result["result"]
    assert isinstance(result["result"]["best_value"], float)


def test_set_backend_fallback(monkeypatch):
    monkeypatch.setattr("quantum.optimizers.quantum_optimizer.init_ibm_backend", lambda **_: (object(), False))
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)])
    opt.set_backend(None, use_hardware=True)
    assert opt.use_hardware is False


@pytest.mark.hardware
def test_set_backend_hardware(monkeypatch):
    backend = object()
    monkeypatch.setattr(
        "quantum.optimizers.quantum_optimizer.init_ibm_backend",
        lambda **_: (backend, True),
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    opt.set_backend(None, use_hardware=True)
    assert opt.use_hardware is True
    assert opt.backend is backend
