import numpy as np

from quantum.optimizers.quantum_optimizer import QuantumOptimizer


def test_simulated_annealing_run():
    def objective(x: np.ndarray) -> float:
        return float(np.sum(x**2))

    opt = QuantumOptimizer(objective, [(-1.0, 1.0), (-1.0, 1.0)], method="simulated_annealing")
    summary = opt.run(x0=np.array([0.2, -0.2]), max_iter=20)
    assert "best_result" in summary["result"]
    assert len(summary["history"]) > 0
