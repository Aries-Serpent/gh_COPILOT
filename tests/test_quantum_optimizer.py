from quantum.quantum_optimization import QuantumOptimizer


def test_quantum_optimizer_runs():
    optimizer = QuantumOptimizer()
    result = optimizer.optimize()
    assert "theta" in result
    assert "expectation" in result
