import numpy as np

from quantum.optimizers.quantum_optimizer import QuantumOptimizer


def test_simulated_annealing_runs():
    def obj(x):
        return np.sum((x - 1) ** 2)

    optimizer = QuantumOptimizer(obj, [(-2, 2), (-2, 2)], method="simulated_annealing")
    result = optimizer.run(x0=np.array([0.0, 0.0]), max_iter=10)
    assert "best_result" in result["result"]
    assert isinstance(result["result"]["best_value"], float)
