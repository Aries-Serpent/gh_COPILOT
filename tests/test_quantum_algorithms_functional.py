import numpy as np

from quantum_algorithms_functional import (run_grover_search,
                                           run_kmeans_clustering,
                                           run_simple_qnn)


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
