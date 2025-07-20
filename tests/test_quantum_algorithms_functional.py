#!/usr/bin/env python3

import logging

from scripts.utilities.quantum_algorithms_functional import (
    run_grover_search,
    run_kmeans_clustering,
    run_simple_qnn,
    run_shor_factorization,
    run_quantum_fourier_transform,
    run_variational_circuit,
    run_quantum_teleportation,
)


def test_run_grover_search_find_index():
    result = run_grover_search([1, 2, 3], 2)
    assert result["index"] == 1
    assert result["iterations"] >= 1


def test_run_kmeans_clustering_returns_inertia():
    metrics = run_kmeans_clustering(samples=20, clusters=2)
    assert metrics["inertia"] >= 0


def test_run_simple_qnn_accuracy_range():
    metrics = run_simple_qnn()
    assert 0.0 <= metrics["accuracy"] <= 1.0


def test_shor_factorization_simple():
    factors = run_shor_factorization(15)
    assert 3 in factors and 5 in factors


def test_quantum_fourier_transform_runs():
    state = run_quantum_fourier_transform([1, 0, 0, 0])
    assert len(state) == 4


def test_variational_circuit_executes():
    result = run_variational_circuit(steps=5, lr=0.2)
    assert "theta" in result and "expectation" in result


def test_quantum_teleportation_preserves_state():
    dm = run_quantum_teleportation([1, 0])
    assert dm[0][0] == 1
