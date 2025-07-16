"""
Quantum functional algorithms with performance metrics.
Refactored from original quantum_algorithms_functional.py with enhanced modularity.
"""

import time
from typing import Any, Dict, List, Optional

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from .base import QuantumAlgorithmBase, TEXT_INDICATORS


class QuantumFunctional(QuantumAlgorithmBase):
    """Collection of functional quantum algorithms with performance metrics"""
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name"""
        return "Quantum Functional Algorithms"
    
    def execute_algorithm(self) -> bool:
        """Execute all functional quantum algorithms"""
        try:
            # Run all three functional algorithms
            grover_result = self.run_grover_search([1, 2, 3, 4], 3)
            kmeans_result = self.run_kmeans_clustering()
            qnn_result = self.run_simple_qnn()
            
            # Log results
            self.logger.info(f"{TEXT_INDICATORS['info']} Grover search result: {grover_result}")
            self.logger.info(f"{TEXT_INDICATORS['info']} KMeans clustering result: {kmeans_result}")
            self.logger.info(f"{TEXT_INDICATORS['info']} QNN classifier result: {qnn_result}")
            
            # Store results in execution stats
            self.execution_stats.update({
                'grover_result': grover_result,
                'kmeans_result': kmeans_result,
                'qnn_result': qnn_result
            })
            
            # Consider successful if all algorithms completed
            return (grover_result.get('index', -1) >= 0 and 
                   kmeans_result.get('inertia', 0) > 0 and
                   qnn_result.get('accuracy', 0) > 0)
            
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Functional algorithms failed: {e}")
            return False

    def run_grover_search(self, data: List[int], target: int) -> Dict[str, Any]:
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
        
        with tqdm(range(iterations), desc=f"{TEXT_INDICATORS['progress']} grover", leave=False) as pbar:
            for _ in pbar:
                oracle(qc)
                diffusion(qc)
                
        qc.measure(range(num_qubits), range(num_qubits))
        backend = AerSimulator()
        counts = backend.run(qc, shots=1024).result().get_counts()
        measured = max(counts, key=counts.get)
        runtime = time.perf_counter() - start_time
        return {"index": int(measured, 2), "time": runtime, "iterations": iterations}

    def run_kmeans_clustering(self, samples: int = 100, clusters: int = 2) -> Dict[str, Any]:
        """Run ``KMeans`` clustering and return inertia and runtime."""
        features, _ = make_blobs(n_samples=samples, centers=clusters, random_state=42)
        start = time.perf_counter()
        model = KMeans(n_clusters=clusters, n_init="auto", random_state=42)
        
        with tqdm(total=1, desc=f"{TEXT_INDICATORS['progress']} kmeans", leave=False) as bar:
            model.fit(features)
            bar.update(1)
            
        runtime = time.perf_counter() - start
        return {"inertia": float(model.inertia_), "time": runtime}

    def run_simple_qnn(self) -> Dict[str, Any]:
        """Train a small QNN classifier and report accuracy."""
        features, labels = make_blobs(n_samples=200, centers=2, random_state=42)
        x_train, x_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.3, random_state=42)
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x_train)
        x_test = scaler.transform(x_test)

        classifier = MLPClassifier(hidden_layer_sizes=(5,), max_iter=200, random_state=42)
        start = time.perf_counter()
        
        with tqdm(total=1, desc=f"{TEXT_INDICATORS['progress']} qnn", leave=False) as bar:
            classifier.fit(x_train, y_train)
            bar.update(1)
            
        accuracy = classifier.score(x_test, y_test)
        runtime = time.perf_counter() - start
        return {"accuracy": float(accuracy), "time": runtime}


def main():
    """Main execution function - maintains backward compatibility"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    functional = QuantumFunctional()
    success = functional.execute_utility()
    
    if success:
        stats = functional.get_execution_stats()
        print("\nAlgorithm Results:")
        if 'grover_result' in stats:
            print(f"  Grover Search: {stats['grover_result']}")
        if 'kmeans_result' in stats:
            print(f"  KMeans Clustering: {stats['kmeans_result']}")  
        if 'qnn_result' in stats:
            print(f"  QNN Classifier: {stats['qnn_result']}")
    
    return success


if __name__ == "__main__":  # pragma: no cover - manual execution
    import sys
    success = main()
    sys.exit(0 if success else 1)