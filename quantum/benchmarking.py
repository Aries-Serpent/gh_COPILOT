"""Benchmark quantum algorithms and load performance metrics."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Dict

from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap

try:
    from qiskit.utils import algorithm_globals

    def _set_seed(seed: int) -> None:
        algorithm_globals.random_seed = seed
except ImportError:  # pragma: no cover - fallback for older qiskit
    import numpy as np

    def _set_seed(seed: int) -> None:
        np.random.seed(seed)
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from physics_optimization_engine import PhysicsOptimizationEngine

try:
    from qiskit import BasicAer

    def _get_backend(name: str):
        return BasicAer.get_backend(name)
except Exception:  # pragma: no cover - for qiskit>=2
    try:
        from qiskit.providers.basic_provider import BasicSimulator

        def _get_backend(name: str):  # pragma: no cover - fallback backend
            return BasicSimulator()
    except Exception:
        _get_backend = None

__all__ = [
    "load_metrics",
    "benchmark_physics_engine",
    "benchmark_qnn",
]


def load_metrics(path: str | Path = "production_performance_validation.json") -> Dict[str, Any]:
    """Load production performance metrics from a JSON file."""
    metrics_path = Path(path)
    with metrics_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def benchmark_physics_engine() -> Dict[str, Any]:
    """Benchmark algorithms from :class:`PhysicsOptimizationEngine`."""
    engine = PhysicsOptimizationEngine()
    results: Dict[str, Any] = {}

    start = perf_counter()
    results["grover_result"] = engine.grover_search([0, 1, 2, 3], 2)
    results["grover_search_time"] = perf_counter() - start

    start = perf_counter()
    results["shor_result"] = engine.shor_factorization(21)
    results["shor_time"] = perf_counter() - start

    start = perf_counter()
    results["fourier_result"] = engine.fourier_transform([1, 0, 0, 0])
    results["fourier_time"] = perf_counter() - start

    return results


def benchmark_qnn() -> Dict[str, float]:
    """Benchmark the QNN predictive maintenance example."""
    try:
        from qiskit_machine_learning.algorithms.classifiers import \
            NeuralNetworkClassifier
        from qiskit_machine_learning.neural_networks import TwoLayerQNN
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("qiskit_machine_learning is required") from exc

    _set_seed(42)

    features, labels = make_classification(
        n_samples=200,
        n_features=2,
        n_informative=2,
        n_redundant=0,
        random_state=42,
    )
    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.3, random_state=42
    )

    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    feature_map = ZZFeatureMap(feature_dimension=2, reps=1)
    ansatz = RealAmplitudes(num_qubits=2, reps=1)
    if _get_backend is None:
        raise RuntimeError("No suitable backend available")
    backend = _get_backend("statevector_simulator")
    qnn = TwoLayerQNN(
        num_qubits=2,
        feature_map=feature_map,
        ansatz=ansatz,
        quantum_instance=backend,
    )

    classifier = NeuralNetworkClassifier(qnn)
    start = perf_counter()
    classifier.fit(x_train, y_train)
    score = classifier.score(x_test, y_test)
    duration = perf_counter() - start

    return {
        "accuracy": float(score),
        "training_time": duration,
    }
