#!/usr/bin/env python3
"""QuantumAlgorithmsFunctional
==============================

Collection of functional quantum algorithms used across the
``gh_COPILOT`` toolkit. Each function returns useful performance
metrics in addition to computational results.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from qiskit_aer import AerSimulator
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from qiskit import QuantumCircuit

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "progress": "[PROGRESS]",
}

logger = logging.getLogger(__name__)


def run_grover_search(data: List[int], target: int) -> Dict[str, Any]:
    """Locate ``target`` in ``data`` using Grover search."""
    start_time = time.perf_counter()
    try:
        index = data.index(target)
    except ValueError:
        return {"index": -1, "time": 0.0, "iterations": 0}
    num_qubits = int(np.ceil(np.log2(len(data))))
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))

    def oracle(circ: QuantumCircuit) -> None:
        for q in range(num_qubits):
            if (index >> q) & 1 == 0:
                circ.x(q)
        if num_qubits == 1:
            circ.z(0)
        else:
            circ.h(num_qubits - 1)
            circ.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circ.h(num_qubits - 1)
        for q in range(num_qubits):
            if (index >> q) & 1 == 0:
                circ.x(q)

    def diffusion(circ: QuantumCircuit) -> None:
        circ.h(range(num_qubits))
        circ.x(range(num_qubits))
        if num_qubits == 1:
            circ.z(0)
        else:
            circ.h(num_qubits - 1)
            circ.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circ.h(num_qubits - 1)
        circ.x(range(num_qubits))
        circ.h(range(num_qubits))

    iterations = max(1, int(np.pi / 4 * np.sqrt(2 ** num_qubits)))
    for _ in tqdm(range(iterations), desc=f"{TEXT_INDICATORS['progress']} grover"):
        oracle(qc)
        diffusion(qc)
    qc.measure(range(num_qubits), range(num_qubits))
    backend = AerSimulator()
    counts = backend.run(qc, shots=1024).result().get_counts()
    measured = max(counts, key=counts.get)
    runtime = time.perf_counter() - start_time
    return {"index": int(measured, 2), "time": runtime, "iterations": iterations}


def run_kmeans_clustering(samples: int = 100, clusters: int = 2) -> Dict[str, Any]:
    """Run ``KMeans`` clustering and return inertia and runtime."""
    features, _ = make_blobs(n_samples=samples, centers=clusters, random_state=42)
    start = time.perf_counter()
    model = KMeans(n_clusters=clusters, n_init="auto", random_state=42)
    with tqdm(total=1, desc=f"{TEXT_INDICATORS['progress']} kmeans") as bar:
        model.fit(features)
        bar.update(1)
    runtime = time.perf_counter() - start
    return {"inertia": float(model.inertia_), "time": runtime}


def run_simple_qnn() -> Dict[str, Any]:
    """Train a small QNN classifier and report accuracy."""
    features, labels = make_blobs(n_samples=200, centers=2, random_state=42)
    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.3, random_state=42)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    classifier = MLPClassifier(hidden_layer_sizes=(5,), max_iter=200, random_state=42)
    start = time.perf_counter()
    with tqdm(total=1, desc=f"{TEXT_INDICATORS['progress']} qnn") as bar:
        classifier.fit(x_train, y_train)
        bar.update(1)
    accuracy = classifier.score(x_test, y_test)
    runtime = time.perf_counter() - start
    return {"accuracy": float(accuracy), "time": runtime}


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    print(run_grover_search([1, 2, 3, 4], 3))
    print(run_kmeans_clustering())
    print(run_simple_qnn())
