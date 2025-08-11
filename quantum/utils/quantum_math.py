"""
Quantum mathematical utilities.
"""

import numpy as np
from typing import Tuple


class QuantumMath:
    """Mathematical utilities for quantum algorithms"""
    
    @staticmethod
    def calculate_grover_iterations(n_items: int) -> int:
        """Calculate optimal number of Grover iterations for n items"""
        if n_items <= 1:
            return 1
        return max(1, int(np.pi / 4 * np.sqrt(n_items)))
    
    @staticmethod
    def calculate_quantum_advantage(classical_time: float, quantum_time: float) -> float:
        """Calculate quantum advantage ratio"""
        if quantum_time == 0:
            return float('inf')
        return classical_time / quantum_time
    
    @staticmethod
    def estimate_quantum_fidelity(counts: dict, expected_state: str) -> float:
        """Estimate quantum fidelity from measurement counts"""
        total_shots = sum(counts.values())
        if total_shots == 0:
            return 0.0
        
        expected_count = counts.get(expected_state, 0)
        return expected_count / total_shots
    
    @staticmethod
    def calculate_success_probability(iterations: int, n_items: int) -> float:
        """Calculate success probability for Grover's algorithm"""
        if n_items <= 1:
            return 1.0
        
        theta = np.arcsin(1 / np.sqrt(n_items))
        angle = (2 * iterations + 1) * theta
        return np.sin(angle) ** 2
    
    @staticmethod
    def optimize_circuit_depth(n_qubits: int, gate_count: int) -> Tuple[int, float]:
        """Estimate optimal circuit depth and error rate"""
        # Simple heuristic for circuit optimization
        optimal_depth = max(1, gate_count // n_qubits)
        error_rate = 1 - np.exp(-gate_count * 0.001)  # Simple error model
        return optimal_depth, error_rate