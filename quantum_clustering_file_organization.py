#!/usr/bin/env python3
"""Quantum Clustering File Organization
=======================================

This script groups files in a directory using a quantum kernel-based
clustering approach. File size and modification time are converted to a
two-dimensional feature space, and a
``FidelityQuantumKernel`` computes the similarity matrix used by
:class:`sklearn.cluster.KMeans`.

The example illustrates how quantum kernels can assist with file
classification and organization tasks.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from qiskit import BasicAer

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]'
}


class EnterpriseUtility:
    """Enterprise utility class"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger(__name__)

    def execute_utility(self) -> bool:
        """Execute utility function"""
        start_time = datetime.now()
        self.logger.info(f"{TEXT_INDICATORS['start']} Utility started: {start_time}")

        try:
            success = self.perform_utility_function()

            if success:
                duration = (datetime.now() - start_time).total_seconds()
                self.logger.info(
                    f"{TEXT_INDICATORS['success']} Utility completed in {duration:.1f}s")
                return True
            else:
                self.logger.error(f"{TEXT_INDICATORS['error']} Utility failed")
                return False

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Utility error: {e}")
            return False

    def perform_utility_function(self) -> bool:
        """Cluster files using a quantum kernel."""
        file_paths = [p for p in self.workspace_path.iterdir() if p.is_file()]
        if not file_paths:
            self.logger.info(f"{TEXT_INDICATORS['info']} No files found")
            return False

        features = [
            [f.stat().st_size, f.stat().st_mtime]
            for f in file_paths
        ]

        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        feature_map = ZZFeatureMap(feature_dimension=2, reps=1)
        backend = BasicAer.get_backend("statevector_simulator")
        kernel = FidelityQuantumKernel(feature_map=feature_map, quantum_instance=backend)
        kernel_matrix = kernel.evaluate(features_scaled)

        kmeans = KMeans(n_clusters=2, random_state=42)
        labels = kmeans.fit_predict(kernel_matrix)

        for path, label in zip(file_paths, labels):
            self.logger.info(f"{TEXT_INDICATORS['info']} {path.name}: cluster {label}")

        return True


def main():
    """Main execution function"""
    utility = EnterpriseUtility()
    success = utility.execute_utility()

    if success:
        print(f"{TEXT_INDICATORS['success']} Utility completed")
    else:
        print(f"{TEXT_INDICATORS['error']} Utility failed")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
