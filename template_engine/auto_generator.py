#!/usr/bin/env python3
"""Simplified template generation engine."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("template_completion.db")



@dataclass
class ClusterModel:
    """Wrapper around :class:`sklearn.cluster.KMeans`."""

    n_clusters: int
    kmeans: KMeans


class TemplateAutoGenerator:
    """Generate templates using simple rules."""

    def __init__(self, analytics_db: Path, completion_db: Path) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()

        all_items = self.templates + self.patterns
        n_clusters = max(1, len(self.templates))
        if all_items:
            self._vectorizer = TfidfVectorizer()
            features = self._vectorizer.fit_transform(all_items)
            kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42)
            kmeans.fit(features)
        else:
            self._vectorizer = None
            kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42)
        self.cluster_model = ClusterModel(n_clusters=n_clusters, kmeans=kmeans)
        self._last_template: str | None = None

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

    def generate_template(self, params: Dict[str, str]) -> str:
        action = params.get("action", "")
        for pattern in self.patterns:
            check_syntax = pattern.strip().startswith(("def", "class", "print"))
            if check_syntax:
                try:
                    compile(pattern, "<pattern>", "exec")
                except SyntaxError as exc:  # pragma: no cover - invalid pattern
                    raise ValueError("Invalid pattern syntax") from exc
            if action and action in pattern:
                self._last_template = pattern
                return pattern
        if self.templates:
            self._last_template = self.templates[0]
            return self.templates[0]
        return ""

    def regenerate_template(self) -> str:
        return self._last_template or ""

    def get_cluster_representatives(self) -> List[str]:
        if not self._vectorizer or not (self.templates or self.patterns):
            return []

        data = self.templates + self.patterns
        features = self._vectorizer.transform(data)
        labels = self.cluster_model.kmeans.labels_
        reps: List[str] = []

        for idx in range(self.cluster_model.n_clusters):
            cluster_indices = np.where(labels == idx)[0]
            if cluster_indices.size == 0:
                continue
            center = self.cluster_model.kmeans.cluster_centers_[idx]
            dists = np.linalg.norm(features[cluster_indices] - center, axis=1)
            nearest_idx = cluster_indices[int(dists.argmin())]
            reps.append(data[nearest_idx])
        return reps

    def objective_similarity(self, a: str, b: str) -> float:
        if not self._vectorizer:
            return 1.0 if a == b else 0.0
        vec = self._vectorizer.transform([a, b])
        sim = float((vec[0] @ vec[1].T).toarray()[0][0])
        return sim

    def select_best_template(self, target: str) -> str:
        if not self.templates:
            return target
        scores = [self.objective_similarity(target, t) for t in self.templates]
        best_idx = int(np.argmax(scores))
        return self.templates[best_idx]
