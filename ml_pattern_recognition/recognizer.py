"""Lightweight ML-based pattern recognition with feedback integration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.lessons_learned_integrator import store_lesson


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

    def learn(self, data: Iterable[str]) -> None:
        """Train the underlying model on ``data``."""
        self.model.fit(data)

    def recognize(self, data: Iterable[str], *, db_path: Path | None = None) -> List[str]:
        """Return recognized patterns from ``data`` and record lessons."""
        predictions = self.model.predict(data)
        timestamp = datetime.utcnow().isoformat()
        for label in predictions:
            kwargs = {}
            if db_path is not None:
                kwargs["db_path"] = db_path
            store_lesson(
                description=f"Detected {label}",
                source="ml_pattern_recognition",
                timestamp=timestamp,
                validation_status="pending",
                tags="pattern_recognition",
                **kwargs,
            )
        return predictions
