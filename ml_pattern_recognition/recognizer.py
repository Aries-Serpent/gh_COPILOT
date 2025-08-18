"""Lightweight ML-based pattern recognition with feedback integration."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.lessons_learned_integrator import store_lessons


"""Pattern recognition utilities backed by production datasets."""


class SklearnPatternModel:
    """Simple TF-IDF + KMeans model for text patterns."""

    def __init__(self, n_clusters: int = 2) -> None:
        self.vectorizer = TfidfVectorizer()
        self.model = KMeans(n_clusters=n_clusters, n_init=10)
        self.trained = False

    def fit(self, data: Iterable[str]) -> None:
        matrix = self.vectorizer.fit_transform(list(data))
        self.model.fit(matrix)
        self.trained = True

    def predict(self, data: Iterable[str]) -> List[str]:
        if not self.trained:
            raise ValueError("Model must be trained before prediction")
        matrix = self.vectorizer.transform(list(data))
        labels = self.model.predict(matrix)
        return [f"cluster_{label}" for label in labels]


class PatternRecognizer:
    """ML-based pattern recognizer with lessons-learned feedback."""

    def __init__(self, model: SklearnPatternModel | None = None) -> None:
        self.model = model or SklearnPatternModel()
        if not (hasattr(self.model, "fit") and hasattr(self.model, "predict")):
            raise TypeError("model must implement fit and predict methods")

    def learn(self, data: Iterable[str]) -> None:
        """Train the underlying model on ``data``."""
        self.model.fit(data)

    def recognize(self, data: Iterable[str], *, db_path: Path | None = None) -> List[str]:
        """Return recognized patterns from ``data`` and record lessons."""
        predictions = self.model.predict(data)
        timestamp = datetime.utcnow().isoformat()
        lessons = [
            {
                "description": f"Detected {label}",
                "source": "ml_pattern_recognition",
                "timestamp": timestamp,
                "validation_status": "pending",
                "tags": "pattern_recognition",
            }
            for label in predictions
        ]
        if db_path is not None:
            store_lessons(lessons, db_path=db_path)
        else:
            store_lessons(lessons)
        return predictions


def load_production_data(path: Path | None = None) -> List[str]:
    """Load training data from a production-ready dataset.

    If ``path`` is ``None`` the function looks for ``ML_PATTERN_DATA_PATH``
    environment variable. Returns a list of non-empty lines.
    """

    if path is None:
        env_path = os.getenv("ML_PATTERN_DATA_PATH")
        if not env_path:
            return []
        path = Path(env_path)

    if not path.exists():
        return []

    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
