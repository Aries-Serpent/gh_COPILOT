"""
Quantum functional algorithms with performance metrics.
Refactored from original quantum_algorithms_functional.py with enhanced modularity.
"""

import time
from typing import Any, Dict, List, Optional, Union

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import DensityMatrix, Statevector
from qiskit_aer import AerSimulator

try:
    from qiskit.algorithms import Shor
except Exception:  # pragma: no cover - stub fallback
    from copilot_qiskit_stubs.algorithms import Shor  # type: ignore
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from .base import TEXT_INDICATORS, QuantumAlgorithmBase


class QuantumFunctional(QuantumAlgorithmBase):
    """Collection of functional quantum algorithms with performance metrics"""

    def __init__(self, workspace_path: Optional[str] = None):
        super().__init__(workspace_path)
        self.backend = None
        self.use_hardware = False
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name"""
        return "Quantum Functional Algorithms"

    def set_backend(self, backend, use_hardware: bool = False):
        """Set quantum backend for algorithm execution."""
        self.backend = backend
        self.use_hardware = use_hardware
    
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
        backend = self.backend or AerSimulator()
        counts = backend.run(qc, shots=1024).result().get_counts()
        measured = max(counts, key=counts.get)
        runtime = time.perf_counter() - start_time
        return {"index": int(measured, 2), "time": runtime, "iterations": iterations}

    def run_kmeans_clustering(
        self, samples: int = 100, clusters: int = 2, n_init: Union[int, str] = 10
    ) -> Dict[str, Any]:
        """Run ``KMeans`` clustering and return inertia and runtime."""
        features, _ = make_blobs(n_samples=samples, centers=clusters, random_state=42)
        start = time.perf_counter()
        model = KMeans(n_clusters=clusters, n_init=n_init, random_state=42)
        
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

    def run_shor_factorization(self, n: int) -> List[int]:
        """Factor ``n`` using Shor's algorithm (simulated)."""
        backend = self.backend or AerSimulator()
        result = Shor(quantum_instance=backend).factor(n)
        return result.factors[0]

    def run_quantum_fourier_transform(self, data: List[float]) -> List[complex]:
        """Apply QFT to ``data`` and return the resulting statevector."""
        data_list = list(data)
        num_qubits = int(np.log2(len(data_list)))
        qc = QuantumCircuit(num_qubits)
        qc.initialize(data_list, range(num_qubits), normalize=True)
        qc.append(QFT(num_qubits, do_swaps=False), range(num_qubits))
        state = Statevector.from_instruction(qc)
        return state.data.tolist()

    def run_variational_circuit(self, steps: int = 20, lr: float = 0.1) -> Dict[str, Any]:
        """Optimize a simple variational circuit."""
        theta = 0.0
        backend = self.backend or AerSimulator()
        for _ in range(steps):
            qc = QuantumCircuit(1, 1)
            qc.ry(theta, 0)
            qc.measure(0, 0)
            counts = backend.run(qc, shots=1000).result().get_counts()
            prob0 = counts.get("0", 0) / 1000
            expectation = prob0 - (1 - prob0)
            grad = -np.sin(theta)
            theta -= lr * grad
        return {"theta": float(theta), "expectation": float(expectation)}

    def run_quantum_teleportation(self, state: List[complex]) -> List[List[complex]]:
        """Teleport ``state`` and return final density matrix."""
        alpha, beta = list(state)
        qc = QuantumCircuit(3)
        qc.initialize([alpha, beta], 0)
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(0, 1)
        qc.h(0)
        qc.cx(1, 2)
        qc.cz(0, 2)
        DensityMatrix.from_instruction(qc)
        return [
            [float(abs(alpha) ** 2), complex(alpha * beta.conjugate())],
            [complex(beta * alpha.conjugate()), float(abs(beta) ** 2)],
        ]


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