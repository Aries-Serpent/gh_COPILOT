import numpy as np

from ghc_quantum.optimizers.quantum_optimizer import QuantumOptimizer
from ghc_quantum.optimizers import quantum_optimizer as qo


def test_run_falls_back_when_hardware_unavailable(monkeypatch):
    monkeypatch.setattr(qo, "IBMProvider", None)

    def obj(x: np.ndarray) -> float:
        return float(np.sum(x**2))

    opt = QuantumOptimizer(obj, [(-1, 1)], method="simulated_annealing", use_hardware=True)
    summary = opt.run(x0=np.array([0.0]), max_iter=5)
    assert "best_result" in summary["result"]
    assert opt.use_hardware is False
