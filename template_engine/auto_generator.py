from __future__ import annotations

import ast
import sqlite3
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("template_completion.db")


class TemplateAutoGenerator:
    """Generate templates from stored patterns using clustering."""

    def __init__(self, analytics_db: Path, completion_db: Path) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.cluster_model = self._create_cluster_model()
        self._last_template: str | None = None

    # ------------------------------------------------------------------
    def _load_patterns(self) -> List[str]:
        if not self.analytics_db.exists():
            return []
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute("SELECT replacement_template FROM ml_pattern_optimization")
            return [row[0] for row in cur.fetchall()]

    def _load_templates(self) -> List[str]:
        if not self.completion_db.exists():
            return []
        with sqlite3.connect(self.completion_db) as conn:
            cur = conn.execute("SELECT template_content FROM templates")
            return [row[0] for row in cur.fetchall()]

    # ------------------------------------------------------------------
    def generate_template(self, config: Dict[str, str]) -> str:
        keyword = next(iter(config.values()), "")
        for text in self.patterns + self.templates:
            if keyword and keyword in text:
                self._validate_template(text)
                self._last_template = text
                return text
        if self.patterns:
            candidate = self.patterns[0]
            self._validate_template(candidate)
            self._last_template = candidate
            return candidate
        self._last_template = ""
        return ""

    def regenerate_template(self) -> str:
        return self._last_template or ""

    # ------------------------------------------------------------------
    def _validate_template(self, text: str) -> None:
        try:
            ast.parse(text)
        except SyntaxError as exc:
            raise ValueError("Invalid template syntax") from exc

    def _create_cluster_model(self) -> KMeans:
        data = self.templates or self.patterns
        if not data:
            return KMeans(n_clusters=1, n_init="auto")
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(data)
        n_clusters = min(len(data), 2)
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
        model.fit(matrix)
        self._vectorizer = vectorizer
        self._matrix = matrix
        return model

    def get_cluster_representatives(self) -> List[str]:
        data = self.templates or self.patterns
        if not data:
            return []
        reps = []
        for idx in range(self.cluster_model.n_clusters):
            indices = np.where(self.cluster_model.labels_ == idx)[0]
            if not len(indices):
                continue
            centroid = self.cluster_model.cluster_centers_[idx]
            best = min(indices, key=lambda i: np.linalg.norm(self._matrix[i].toarray() - centroid))
            reps.append(data[best])
        return reps
