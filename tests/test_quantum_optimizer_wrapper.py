import numpy as np

from ghc_quantum.optimizers.quantum_optimizer import QuantumOptimizer


def objective(x: np.ndarray) -> float:
    return float(np.sum((x - 1.0) ** 2))


def test_simulated_annealing_runs():
    opt = QuantumOptimizer(objective, [(-2, 2), (-2, 2)], method="simulated_annealing")
    result = opt.run(x0=np.array([0.0, 0.0]), max_iter=10)
    assert "best_result" in result["result"]
    assert len(opt.history) > 0
