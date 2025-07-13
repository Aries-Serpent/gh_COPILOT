"""Automatic template generation using stored patterns."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import ast

from sklearn.metrics.pairwise import cosine_distances

from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("databases/template_completion.db")


class TemplateAutoGenerator:
    """Load patterns from databases and generate templates."""

    def __init__(
        self,
        analytics_db: Path = DEFAULT_ANALYTICS_DB,
        completion_db: Path = DEFAULT_COMPLETION_DB,
    ) -> None:
        self.analytics_db = analytics_db
        self.completion_db = completion_db
        self.patterns: List[str] = self._load_patterns()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.generated_history: List[str] = []
        if self.patterns:
            self.pattern_matrix = self.vectorizer.fit_transform(self.patterns)
            self.cluster_model = self._cluster_patterns(self.pattern_matrix)
            self.neighbor_model = NearestNeighbors(metric="cosine")
            self.neighbor_model.fit(self.pattern_matrix)
        else:
            self.pattern_matrix = None
            self.cluster_model = None
            self.neighbor_model = None

    def _load_patterns(self) -> List[str]:
        patterns: List[str] = []
        if self.analytics_db.exists():
            with sqlite3.connect(self.analytics_db) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT replacement_template FROM ml_pattern_optimization"
                )
                patterns.extend(row[0] for row in cursor.fetchall() if row[0])
        if self.completion_db.exists():
            with sqlite3.connect(self.completion_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT template_content FROM templates")
                patterns.extend(row[0] for row in cursor.fetchall() if row[0])
        return patterns

    @staticmethod
    def _cluster_patterns(matrix) -> MiniBatchKMeans:
        n_samples = matrix.shape[0]
        n_clusters = min(n_samples, max(2, min(50, n_samples // 100 or 1)))
        model = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
        model.fit(matrix)
        return model

    @staticmethod
    def _validate_syntax(template: str) -> bool:
        """Return ``True`` if ``template`` is valid Python syntax."""
        try:
            ast.parse(template)
        except SyntaxError:
            return False
        return True

    def get_cluster_representatives(self) -> List[str]:
        """Return templates closest to each cluster center."""
        if self.cluster_model is None or self.pattern_matrix is None:
            return []
        representatives: List[str] = []
        centers = self.cluster_model.cluster_centers_
        labels = self.cluster_model.labels_
        for cluster_id in range(self.cluster_model.n_clusters):
            indices = [i for i, label in enumerate(labels) if label == cluster_id]
            if not indices:
                continue
            cluster_vecs = self.pattern_matrix[indices]
            center = centers[cluster_id].reshape(1, -1)
            dists = cosine_distances(cluster_vecs, center).reshape(-1)
            best_local_idx = indices[int(dists.argmin())]
            candidate = self.patterns[best_local_idx]
            if self._validate_syntax(candidate):
                representatives.append(candidate)
        return representatives

    def generate_template(self, target_requirements: Dict[str, Any]) -> str:
        """Return the best matching template for ``target_requirements``."""
        if not self.patterns or self.neighbor_model is None:
            return ""
        query = json.dumps(target_requirements, sort_keys=True)
        query_vec = self.vectorizer.transform([query])
        distances, indices = self.neighbor_model.kneighbors(query_vec, n_neighbors=1)
        best_index = indices[0][0]
        candidate = self.patterns[best_index]
        if not self._validate_syntax(candidate):
            raise ValueError("Generated template has invalid syntax")
        self.generated_history.append(candidate)
        return candidate

    def regenerate_template(self, history_index: int = -1) -> str:
        """Return a previously generated template identified by ``history_index``."""
        if not self.generated_history:
            return ""
        template = self.generated_history[history_index]
        if not self._validate_syntax(template):
            raise ValueError("Stored template has invalid syntax")
        return template


_default_generator: Optional[TemplateAutoGenerator] = None


def generate_template(target_requirements: Dict[str, Any]) -> str:
    """Generate a template using default databases."""
    global _default_generator
    if _default_generator is None:
        _default_generator = TemplateAutoGenerator()
    return _default_generator.generate_template(target_requirements)
