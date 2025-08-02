import numpy as np
import pytest
from quantum.optimizers import quantum_optimizer as qo


def objective(x: np.ndarray) -> float:
    return float(np.sum((x - 1) ** 2))


def test_simulated_annealing():
    opt = qo.QuantumOptimizer(objective, [(-2, 2), (-2, 2)], method="simulated_annealing")
    summary = opt.run(max_iter=5)
    assert "best_result" in summary["result"]


def test_basin_hopping():
    opt = qo.QuantumOptimizer(objective, [(-2, 2)], method="basin_hopping")
    summary = opt.run(x0=np.array([0.0]), niter=5)
    assert "best_result" in summary["result"]


@pytest.mark.skipif(not qo.QISKIT_AVAILABLE, reason="Qiskit not installed")
def test_qaoa():
    opt = qo.QuantumOptimizer(objective, [(-2, 2)], method="qaoa")
    summary = opt.run(n_qubits=2)
    assert "statevector" in summary["result"]


@pytest.mark.skipif(not qo.QISKIT_AVAILABLE, reason="Qiskit not installed")
def test_vqe():
    opt = qo.QuantumOptimizer(objective, [(-2, 2)], method="vqe")
    summary = opt.run(n_qubits=2)
    assert "statevector" in summary["result"]
