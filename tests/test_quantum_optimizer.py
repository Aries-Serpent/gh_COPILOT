from math import pi

from quantum.quantum_optimization import (ANGLE_RESOLUTION, SEARCH_RANGE,
                                          QuantumOptimizer)


def test_quantum_optimizer_runs():
    optimizer = QuantumOptimizer()
    result = optimizer.optimize()
    assert "theta" in result
    assert "expectation" in result


def test_quantum_constants():
    assert abs(ANGLE_RESOLUTION - pi / 8) < 1e-9
    assert SEARCH_RANGE == 16