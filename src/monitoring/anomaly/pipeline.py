"""Training and evaluation pipeline for anomaly detection models."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict
from ..anomaly_detector import MetricModel, detect_anomalies, train_models


class AnomalyPipeline:
    """Pipeline that trains models and evaluates new metrics.

    Parameters
    ----------
    model_path:
        Location where the trained models will be stored.
    """

    def __init__(self, model_path: Path) -> None:
        self.model_path = Path(model_path)
        self.models: Dict[str, MetricModel] | None = None

    def train(self, db_path: Path) -> Dict[str, MetricModel]:
        """Train models from historical metrics in ``db_path`` and persist them."""
        self.models = train_models(db_path)
        with self.model_path.open("wb") as fh:
            pickle.dump(self.models, fh)
        return self.models

    def load(self) -> Dict[str, MetricModel]:
        """Load previously trained models from :attr:`model_path`."""
        with self.model_path.open("rb") as fh:
            self.models = pickle.load(fh)
        return self.models

    def evaluate(self, data: Dict[str, float]) -> Dict[str, bool]:
        """Detect anomalies for current ``data`` using trained models."""
        if self.models is None:
            self.load()
        return detect_anomalies(data, self.models)
