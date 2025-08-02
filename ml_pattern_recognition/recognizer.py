"""Lightweight ML-based pattern recognition with feedback integration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import joblib
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.lessons_learned_integrator import store_lesson


class SklearnPatternModel:
    """TF-IDF + KMeans model with persistence support."""

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

    def save(self, path: Path) -> None:
        """Persist model and vectorizer to ``path``."""
        joblib.dump({"vectorizer": self.vectorizer, "model": self.model}, path)

    @classmethod
    def load(cls, path: Path) -> "SklearnPatternModel":
        """Load model and vectorizer from ``path``."""
        data = joblib.load(path)
        instance = cls()
        instance.vectorizer = data["vectorizer"]
        instance.model = data["model"]
        instance.trained = True
        return instance


def train_pipeline(data: Iterable[str], model_path: Path, *, n_clusters: int = 2) -> SklearnPatternModel:
    """Train ``SklearnPatternModel`` and persist it to ``model_path``."""
    model = SklearnPatternModel(n_clusters=n_clusters)
    model.fit(data)
    model.save(model_path)
    return model


class PatternRecognizer:
    """ML-based pattern recognizer with lessons-learned feedback.

    Parameters
    ----------
    model:
        Optional preconfigured :class:`SklearnPatternModel` instance. If ``None``
        and ``model_path`` exists, the model is loaded from disk. Otherwise a new
        model is created.
    model_path:
        Location where the model should be persisted. Defaults to
        ``artifacts/pattern_model.joblib``.
    """

    def __init__(
        self,
        model: SklearnPatternModel | None = None,
        model_path: Path | None = None,
    ) -> None:
        self.model_path = model_path or Path("artifacts/pattern_model.joblib")
        if model is not None:
            self.model = model
        elif self.model_path.exists():
            self.model = SklearnPatternModel.load(self.model_path)
        else:
            self.model = SklearnPatternModel()

    def learn(self, data: Iterable[str]) -> None:
        """Train the underlying model on ``data``."""
        self.model.fit(data)
        try:
            self.model.save(self.model_path)
        except Exception:
            # Persisting the model is a best-effort operation; ignore failures
            pass

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
