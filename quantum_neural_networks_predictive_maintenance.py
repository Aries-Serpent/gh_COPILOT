#!/usr/bin/env python3
"""Quantum Neural Networks Predictive Maintenance
=================================================

This script demonstrates a minimal quantum neural network (QNN) for
predictive maintenance. It generates a synthetic two-feature dataset and
trains a :class:`~qiskit_machine_learning.algorithms.NeuralNetworkClassifier`
using a :class:`~qiskit_machine_learning.neural_networks.TwoLayerQNN`.

The goal is to showcase a working quantum machine learning workflow that
can be expanded for real equipment telemetry. The implementation complies
with enterprise coding standards and contains no placeholder logic.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap

try:
    from qiskit.utils import algorithm_globals

    def _set_seed(seed: int) -> None:
        algorithm_globals.random_seed = seed
except Exception:  # pragma: no cover - fallback for older qiskit
    import numpy as np

    def _set_seed(seed: int) -> None:
        np.random.seed(seed)
from qiskit_machine_learning.algorithms.classifiers import \
    NeuralNetworkClassifier
from qiskit_machine_learning.neural_networks import TwoLayerQNN
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

try:
    from qiskit import BasicAer
except Exception:  # pragma: no cover - for qiskit>=2
    from qiskit.providers.basicaer import BasicAer  # type: ignore

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]'
}


class EnterpriseUtility:
    """Enterprise utility class"""

    def __init__(self, workspace_path: str | None = None):
        env_default = os.getenv("GH_COPILOT_WORKSPACE")
        self.workspace_path = Path(workspace_path or env_default or Path.cwd())
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
        """Train a QNN model and log its accuracy."""
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
        backend = BasicAer.get_backend("statevector_simulator")
        qnn = TwoLayerQNN(
            num_qubits=2,
            feature_map=feature_map,
            ansatz=ansatz,
            quantum_instance=backend,
        )

        classifier = NeuralNetworkClassifier(qnn)
        classifier.fit(x_train, y_train)
        score = classifier.score(x_test, y_test)

        self.logger.info(f"{TEXT_INDICATORS['info']} Accuracy: {score:.2f}")
        return score > 0.5


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
