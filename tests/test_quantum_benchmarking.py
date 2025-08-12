#!/usr/bin/env python3

import pytest
from qiskit_machine_learning.neural_networks import EstimatorQNN

from ghc_quantum import benchmarking as benchmarking_module
from ghc_quantum.benchmarking import benchmark_physics_engine, benchmark_qnn, load_metrics


def test_load_metrics():
    metrics = load_metrics("production_performance_validation.json")
    assert "response_time_sla" in metrics


def test_benchmark_physics_engine():
    results = benchmark_physics_engine()
    assert results["grover_result"] == 2
    assert "grover_search_time" in results


def test_benchmark_qnn():
    pytest.importorskip("qiskit_machine_learning")
    try:
        results = benchmark_qnn()
    except ImportError:
        pytest.skip("qiskit_machine_learning backend unavailable")
    assert 0.0 <= results["accuracy"] <= 1.0


def test_benchmarking_uses_estimator_qnn():
    pytest.importorskip("qiskit_machine_learning")
    assert benchmarking_module.EstimatorQNN is EstimatorQNN
