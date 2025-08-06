"""Production-backed ML pattern recognition utilities.

This module now loads sample training data directly from ``production.db`` and
optionally computes quantum-aware evaluation metrics using
``quantum_algorithm_library_expansion.quantum_similarity_score``.
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder


def load_production_data(
    db_path: Path | str = Path("databases/production.db"),
) -> Tuple[np.ndarray, np.ndarray]:
    """Load training data from the ``solution_patterns`` table.

    Parameters
    ----------
    db_path:
        Path to the SQLite database. Defaults to ``databases/production.db``.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Feature matrix ``X`` with columns ``effectiveness_score`` and
        ``usage_count`` and label vector ``y`` with pattern categories.
    """

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT effectiveness_score, usage_count, category FROM solution_patterns"
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        raise ValueError("No data found in solution_patterns table")

    X = np.array([[r[0], r[1]] for r in rows], dtype=float)
    y = np.array([r[2] for r in rows])
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

    def evaluate(self, X: np.ndarray, y: np.ndarray, *, use_quantum: bool = False) -> dict:
        """Return evaluation metrics for provided data.

        Parameters
        ----------
        X, y:
            Dataset used for evaluation.
        use_quantum:
            When ``True`` a quantum similarity score is computed using
            :func:`quantum_algorithm_library_expansion.quantum_similarity_score`.
        """

        preds = self.predict(X)
        result = {"accuracy": float(accuracy_score(y, preds))}

        if use_quantum:
            from quantum_algorithm_library_expansion import quantum_similarity_score

            encoder = LabelEncoder()
            encoder.fit(np.concatenate([preds, y]))
            result["quantum_score"] = quantum_similarity_score(
                encoder.transform(preds), encoder.transform(y)
            )

        return result
