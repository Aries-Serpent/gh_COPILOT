#!/usr/bin/env python3
from quantum_algorithm_library_expansion import (
    EnterpriseUtility,
    demo_grover_search,
    demo_shor_factorization,
    demo_quantum_fourier_transform,
    demo_variational_quantum_eigensolver,
    demo_quantum_phase_estimation,
    demo_quantum_teleportation,
    quantum_cluster_score,
    demo_quantum_neural_network,
)
import numpy as np


def test_perform_utility_function_runs():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True


def test_demo_grover_search_returns_int():
    result = demo_grover_search()
    assert isinstance(result, int)


def test_demo_quantum_teleportation():
    dm = demo_quantum_teleportation()
    assert len(dm) == 2 and len(dm[0]) == 2


def test_demo_quantum_fourier_transform():
    vec = demo_quantum_fourier_transform()
    assert len(vec) == 4


def test_demo_shor_factorization():
    factors = demo_shor_factorization(15)
    assert 3 in factors and 5 in factors


def test_demo_variational_quantum_eigensolver():
    result = demo_variational_quantum_eigensolver(steps=5, lr=0.2)
    assert "theta" in result and "energy" in result


def test_demo_quantum_phase_estimation():
    estimate = demo_quantum_phase_estimation(0.3, precision=3)
    assert abs(estimate - 0.3) <= 0.125


def test_quantum_cluster_score():
    vecs = np.array([[1, 0], [0, 1]], dtype=float)
    score = quantum_cluster_score(vecs)
    assert score > 0


def test_demo_quantum_neural_network():
    data = [1.0, 2.0, 3.0]
    result = demo_quantum_neural_network(data)
    assert len(result) == len(data)
