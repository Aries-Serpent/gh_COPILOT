import numpy as np

from quantum.quantum_optimization import QuantumOptimizer


def test_quantum_optimizer_runs():
    optimizer = QuantumOptimizer()
    result = optimizer.optimize()
    assert "theta" in result
    assert "expectation" in result


def test_grover_search():
    optimizer = QuantumOptimizer()
    result = optimizer.grover_search("11")
    assert result["result"] == "11"


def test_shor_factorization():
    optimizer = QuantumOptimizer()
    factors = optimizer.shor_factorization(15)
    assert set(factors) == {3, 5}


def test_quantum_fourier():
    optimizer = QuantumOptimizer()
    state = optimizer.quantum_fourier(3, 1)
    assert len(state) == 8
    assert abs(state[0] - (1 / np.sqrt(8))) < 1e-6


def test_quantum_clustering():
    optimizer = QuantumOptimizer()
    data = np.array([[0.1, 0.2], [0.9, 0.8], [0.15, 0.25], [0.85, 0.75]])
    labels = optimizer.quantum_clustering(data, k=2, iterations=2)
    assert labels == [0, 1, 0, 1]


def test_quantum_neural_network():
    optimizer = QuantumOptimizer()
    result = optimizer.quantum_neural_network(epochs=5)
    assert result["accuracy"] >= 0.75
