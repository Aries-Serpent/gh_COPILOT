"""
Quantum algorithm library expansion functionality.
Refactored from original quantum_algorithm_library_expansion.py with enhanced modular design.
"""

import os
from pathlib import Path
from typing import Optional

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from .base import QuantumAlgorithmBase, TEXT_INDICATORS
from ..utils import get_backend


class QuantumLibraryExpansion(QuantumAlgorithmBase):
    """Quantum algorithm library expansion with Grover search demonstration"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        if workspace_path is None:
            workspace_path = os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))
        super().__init__(workspace_path)
        self.backend = None
        self.use_hardware = False
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name"""
        return "Quantum Library Expansion"

    def set_backend(self, backend, use_hardware: bool = False):
        """Set quantum backend for execution."""
        self.backend = backend
        self.use_hardware = use_hardware
    
    def execute_algorithm(self) -> bool:
        """Execute quantum library expansion demonstration"""
        return self.perform_grover_demo()
    
    def perform_grover_demo(self) -> bool:
        """Demonstrate Grover search on a 2-qubit system."""
        self.logger.info(f"{TEXT_INDICATORS['info']} Running Grover demo")

        try:
            circuit = QuantumCircuit(2, 2)
            circuit.h([0, 1])
            circuit.cz(0, 1)
            circuit.h([0, 1])
            circuit.x([0, 1])
            circuit.h(1)
            circuit.cx(0, 1)
            circuit.h(1)
            circuit.x([0, 1])
            circuit.h([0, 1])
            circuit.measure([0, 1], [0, 1])

            backend = self.backend
            if backend is None:
                if self.use_hardware:
                    backend = get_backend(use_hardware=True)
                else:
                    backend = AerSimulator()
            if backend is None:
                self.logger.error(f"{TEXT_INDICATORS['error']} No backend available")
                return False
            result = backend.run(circuit, shots=200).result()
            counts = result.get_counts()
            self.logger.info(f"{TEXT_INDICATORS['info']} Counts: {counts}")

            top = max(counts, key=counts.get)
            success = top == "11"
            
            if success:
                self.logger.info(f"{TEXT_INDICATORS['success']} Grover demo successful - found target state {top}")
            else:
                self.logger.info(f"{TEXT_INDICATORS['info']} Grover demo completed - most probable state: {top}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Grover demo failed: {e}")
            return False


def main():
    """Main execution function - maintains backward compatibility"""
    utility = QuantumLibraryExpansion()
    success = utility.execute_utility()

    if success:
        print(f"{TEXT_INDICATORS['success']} Utility completed")
    else:
        print(f"{TEXT_INDICATORS['error']} Utility failed")

    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)