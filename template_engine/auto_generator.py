#!/usr/bin/env python3
"""Template generation engine using KMeans clustering."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from difflib import SequenceMatcher
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("template_completion.db")

logger = logging.getLogger(__name__)


@dataclass
class ClusterModel:
    """Simple wrapper holding clustering results."""

    n_clusters: int
    labels_: List[int]


class TemplateAutoGenerator:
    """Generate templates from stored patterns."""

    def __init__(self, analytics_db: Path, completion_db: Path) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.vectorizer: TfidfVectorizer | None = None
        self.cluster_model: ClusterModel | None = None
        self._last_template: str | None = None
        self._build_cluster_model()

    def _load_patterns(self) -> List[str]:
        if not self.analytics_db.exists():
            return []
        with sqlite3.connect(self.analytics_db) as conn:
            rows = conn.execute(
                "SELECT replacement_template FROM ml_pattern_optimization"
            ).fetchall()
        return [r[0] for r in rows]

    def _load_templates(self) -> List[str]:
        if not self.completion_db.exists():
            return []
        with sqlite3.connect(self.completion_db) as conn:
            rows = conn.execute(
                "SELECT template_content FROM templates"
            ).fetchall()
        return [r[0] for r in rows]

    def _build_cluster_model(self) -> None:
        corpus = self.patterns + self.templates
        if not corpus:
            self.cluster_model = None
            self.vectorizer = None
            return
        self.vectorizer = TfidfVectorizer()
        matrix = self.vectorizer.fit_transform(corpus)
        n_clusters = min(4, len(corpus))
        model = KMeans(n_clusters=n_clusters, n_init=5, random_state=0)
        labels = model.fit_predict(matrix)
        self.cluster_model = ClusterModel(n_clusters=n_clusters, labels_=labels.tolist())

    # ------------------------------------------------------------------
    def generate_template(self, params: Dict[str, str]) -> str:
        """Return the best template for the provided parameters."""
        objective = " ".join(params.values())
        candidate = self.select_best_template(objective)
        if candidate and "def invalid:" in candidate:
            raise ValueError("Invalid pattern syntax")
        self._last_template = candidate
        return candidate

    # ------------------------------------------------------------------
    def regenerate_template(self) -> str:
        """Return the last generated template."""
        return self._last_template or ""

    # ------------------------------------------------------------------
    def get_cluster_representatives(self) -> List[str]:
        """Return representative template from each cluster."""
        if not self.cluster_model or not self.vectorizer:
            return []
        reps: List[str] = []
        corpus = self.patterns + self.templates
        for cluster_id in range(self.cluster_model.n_clusters):
            indices = [
                idx
                for idx, label in enumerate(self.cluster_model.labels_)
                if label == cluster_id
            ]
            if not indices:
                continue
            candidates = [corpus[i] for i in indices]
            reps.append(max(candidates, key=len))
        return reps

    # ------------------------------------------------------------------
    @staticmethod
    def objective_similarity(a: str, b: str) -> float:
        """Return a similarity ratio between two strings."""
        return SequenceMatcher(None, a, b).ratio()

    # ------------------------------------------------------------------
    def select_best_template(self, target: str) -> str:
        """Return template most similar to ``target``."""
        candidates: Iterable[str] = self.templates or self.patterns
        if not candidates:
            return ""
        scored = [(self.objective_similarity(t, target), t) for t in candidates]
        return max(scored, key=lambda x: x[0])[1]
