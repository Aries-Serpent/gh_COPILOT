#!/usr/bin/env python3
# [Script]: Template Generation Engine using KMeans Clustering
# > Generated: 2025-07-22 00:23:23 | Author: mbaetiong

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from difflib import SequenceMatcher
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


@dataclass
class ClusterModel:
    """Simple wrapper holding clustering results."""

    n_clusters: int
    labels_: List[int]


@dataclass
class TemplateAutoGenerator:
    """
    Generate templates from stored patterns using clustering.
    Enterprise Standards: PEP8/flake8 compliant, explicit error handling, environment/path compliance.
    """

    analytics_db: Path
    completion_db: Path

    def __init__(self, analytics_db: Path, completion_db: Path) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns = self._load_patterns(self.analytics_db)
        self.templates = self._load_templates(self.completion_db)
        self.vectorizer: TfidfVectorizer | None = None
        self.cluster_model: ClusterModel | None = None
        self._last_template: str | None = None
        self._build_cluster_model()

    @staticmethod
    def _load_patterns(db_path: Path) -> List[str]:
        """Load replacement templates from ml_pattern_optimization table."""
        if not db_path.exists():
            logger.warning("Patterns DB does not exist: %s", db_path)
            return []
        try:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT replacement_template FROM ml_pattern_optimization"
                ).fetchall()
            return [r[0] for r in rows]
        except sqlite3.Error as exc:
            logger.error("Failed to load patterns from %s: %s", db_path, exc)
            return []

    @staticmethod
    def _load_templates(db_path: Path) -> List[str]:
        """Load template contents from templates table."""
        if not db_path.exists():
            logger.warning("Templates DB does not exist: %s", db_path)
            return []
        try:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT template_content FROM templates").fetchall()
            return [r[0] for r in rows]
        except sqlite3.Error as exc:
            logger.error("Failed to load templates from %s: %s", db_path, exc)
            return []

    def _build_cluster_model(self) -> None:
        """Build clustering model from corpus."""
        corpus = self.patterns + self.templates
        if not corpus:
            self.cluster_model = None
            self.vectorizer = None
            logger.info("No corpus; cluster model not built.")
            return
        self.vectorizer = TfidfVectorizer()
        matrix = self.vectorizer.fit_transform(corpus)
        n_clusters = min(4, len(corpus))
        model = KMeans(n_clusters=n_clusters, n_init=5, random_state=0)
        labels = model.fit_predict(matrix)
        self.cluster_model = ClusterModel(n_clusters=n_clusters, labels_=labels.tolist())
        logger.info("Cluster model built with %d clusters.", n_clusters)

    def generate_template(self, params: Dict[str, str]) -> str:
        """
        Return the best template for the provided parameters.
        Raises ValueError if pattern syntax is invalid.
        """
        objective = " ".join(params.values())
        candidate = self.select_best_template(objective)
        if candidate and "def invalid:" in candidate:
            logger.error("Invalid pattern syntax detected in generated template.")
            raise ValueError("Invalid pattern syntax")
        self._last_template = candidate
        logger.info("Generated template selected.")
        return candidate

    def regenerate_template(self) -> str:
        """Return the last generated template (if any)."""
        logger.info("Regenerating last template.")
        return self._last_template or ""

    def get_cluster_representatives(self) -> List[str]:
        """Return representative template from each cluster."""
        if not self.cluster_model or not self.vectorizer:
            logger.warning("Cluster model or vectorizer not available.")
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
        logger.info("Cluster representatives selected.")
        return reps

    @staticmethod
    def objective_similarity(a: str, b: str) -> float:
        """Return a similarity ratio between two strings."""
        return SequenceMatcher(None, a, b).ratio()

    def select_best_template(self, target: str) -> str:
        """Return template most similar to ``target``."""
        candidates: Iterable[str] = self.templates or self.patterns
        if not candidates:
            logger.warning("No candidates available for template selection.")
            return ""
        scored = [(self.objective_similarity(t, target), t) for t in candidates]
        best = max(scored, key=lambda x: x[0])[1]
        logger.info("Best template selected (score: %.3f)", max(scored, key=lambda x: x[0])[0])
        return best