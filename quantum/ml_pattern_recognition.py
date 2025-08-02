"""Pattern recognition utilities using placeholder datasets."""

from typing import Tuple

import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def load_placeholder_data(
    n_samples: int = 100,
    n_features: int = 4,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate a simple classification dataset for demonstrations."""
    X, y = make_classification(
        n_samples=n_samples, n_features=n_features, random_state=random_state
    )
    return X, y


class PatternRecognizer:
    """Trainable pattern recognizer with logistic regression backend."""

    def __init__(self) -> None:
        self.model = LogisticRegression()
        self.trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the model on data."""
        self.model.fit(X, y)
        self.trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels for ``X``.

        Raises:
            RuntimeError: If called before training.
        """
        if not self.trained:
            raise RuntimeError("Model not trained")
        return self.model.predict(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        """Return accuracy score on provided data."""
        preds = self.predict(X)
        return float(accuracy_score(y, preds))
