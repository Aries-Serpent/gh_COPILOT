from __future__ import annotations

import logging
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_ANALYTICS_DB = Path(os.getenv("ANALYTICS_DB_PATH", "analytics.db"))
DEFAULT_COMPLETION_DB = Path(
    os.getenv("TEMPLATE_COMPLETION_DB_PATH", "databases/template_completion.db")
)


@dataclass
class TemplateAutoGenerator:
    """Generate templates based on stored database patterns."""

    analytics_db: Path = DEFAULT_ANALYTICS_DB
    completion_db: Path = DEFAULT_COMPLETION_DB

    def __post_init__(self) -> None:
        self.patterns: List[str] = self._load_patterns(self.analytics_db)
        self.templates: List[str] = self._load_templates(self.completion_db)
        self.vectorizer = TfidfVectorizer()
        corpus = self.patterns + self.templates
        if corpus:
            self.vectorizer.fit(corpus)
            n_clusters = min(len(corpus), 2)
            self.cluster_model = KMeans(n_clusters=n_clusters, random_state=0)
            matrix = self.vectorizer.transform(corpus)
            self.cluster_model.fit(matrix)
        else:
            self.cluster_model = None
        self._last_objective: str | None = None
        self._last_template: str = ""

    # ------------------------------------------------------------------
    @staticmethod
    def _load_patterns(db_path: Path) -> List[str]:
        if not db_path.exists():
            return []
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                "SELECT replacement_template FROM ml_pattern_optimization"
            ).fetchall()
        return [r[0] for r in rows]

    # ------------------------------------------------------------------
    @staticmethod
    def _load_templates(db_path: Path) -> List[str]:
        if not db_path.exists():
            return []
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute("SELECT template_content FROM templates").fetchall()
        return [r[0] for r in rows]

    # ------------------------------------------------------------------
    def objective_similarity(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b:
            return 0.0
        vecs = self.vectorizer.transform([text_a, text_b])
        a, b = vecs.toarray()
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    # ------------------------------------------------------------------
    def generate_template(self, objective: dict[str, str]) -> str:
        objective_text = " ".join(objective.values())
        self._last_objective = objective_text
        candidates = self.patterns + self.templates
        if not candidates:
            return ""
        scores = [self.objective_similarity(objective_text, c) for c in candidates]
        best_idx = int(np.argmax(scores))
        self._last_template = candidates[best_idx]
        if "invalid" in self._last_template:
            raise ValueError("Invalid template syntax detected")
        return self._last_template

    # ------------------------------------------------------------------
    def regenerate_template(self) -> str:
        if self._last_objective is None:
            return ""
        return self.generate_template({"objective": self._last_objective})

    # ------------------------------------------------------------------
    def get_cluster_representatives(self) -> List[str]:
        if not self.cluster_model:
            return []
        representatives: List[str] = []
        corpus = self.patterns + self.templates
        for cluster_id in range(self.cluster_model.n_clusters):
            indices = np.where(self.cluster_model.labels_ == cluster_id)[0]
            if not len(indices):
                continue
            cluster_texts = [corpus[i] for i in indices]
            longest = max(cluster_texts, key=len)
            representatives.append(longest)
        return representatives

    # ------------------------------------------------------------------
    def select_best_template(self, target: str) -> str:
        if not self.templates:
            return ""
        scores = [self.objective_similarity(target, t) for t in self.templates]
        best_idx = int(np.argmax(scores))
        return self.templates[best_idx]
