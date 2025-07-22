from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import logging
import numpy as np

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from quantum_algorithm_library_expansion import demo_quantum_fourier_transform

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("databases/template_completion.db")

logger = logging.getLogger(__name__)


@dataclass
class TemplateAutoGenerator:
    """Generate and cluster templates loaded from SQLite databases."""

    analytics_db: Path = DEFAULT_ANALYTICS_DB
    completion_db: Path = DEFAULT_COMPLETION_DB

    def __post_init__(self) -> None:
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.cluster_model = self._cluster_patterns()
        self._last_objective: dict | None = None

    # ------------------------------------------------------------------
    def _load_patterns(self) -> List[str]:
        if not self.analytics_db.exists():
            return []
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT replacement_template FROM ml_pattern_optimization"
            )
            return [row[0] for row in cur.fetchall()]

    # ------------------------------------------------------------------
    def _load_templates(self) -> List[str]:
        if not self.completion_db.exists():
            return []
        with sqlite3.connect(self.completion_db) as conn:
            cur = conn.execute("SELECT template_content FROM templates")
            return [row[0] for row in cur.fetchall()]

    # ------------------------------------------------------------------
    def _quantum_score(self, text: str) -> float:
        """Return a quantum-inspired score for ``text``."""
        vec = np.array(demo_quantum_fourier_transform())
        baseline = np.ones_like(vec) / np.sqrt(len(vec))
        return float(abs(np.dot(vec, baseline.conj())))

    # ------------------------------------------------------------------
    def _cluster_patterns(self) -> KMeans | None:
        corpus = self.templates + self.patterns
        if not corpus:
            return None
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(corpus)
        n_clusters = min(len(corpus), 2)
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
        for _ in range(1):
            model.fit(matrix)
        logger.info(
            "[PROGRESS] clustered %s items into %s groups", len(corpus), n_clusters
        )
        return model

    # ------------------------------------------------------------------
    def objective_similarity(self, a: str, b: str) -> float:
        vectorizer = TfidfVectorizer().fit([a, b])
        vecs = vectorizer.transform([a, b])
        return float(cosine_similarity(vecs[0], vecs[1])[0][0])

    # ------------------------------------------------------------------
    def select_best_template(self, target: str) -> str:
        candidates = self.templates if self.templates else self.patterns
        if not candidates:
            return ""
        scores = [
            self.objective_similarity(target, c) + self._quantum_score(c)
            for c in candidates
        ]
        best_idx = int(max(range(len(scores)), key=scores.__getitem__))
        best = candidates[best_idx]
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS template_events (ts TEXT, target TEXT, template TEXT)",
                )
                conn.execute(
                    "INSERT INTO template_events (ts, target, template) VALUES (?,?,?)",
                    (datetime.utcnow().isoformat(), target, best),
                )
        except sqlite3.Error:
            logger.warning("Failed to log template selection")
        return best

    # ------------------------------------------------------------------
    def generate_template(self, objective: dict) -> str:
        self._last_objective = objective
        search_terms = " ".join(map(str, objective.values()))
        start = datetime.utcnow()
        for tmpl in tqdm(
            self.templates + self.patterns, desc="[PROGRESS] search", unit="tmpl"
        ):
            if all(term.lower() in tmpl.lower() for term in search_terms.split()):
                if "def invalid" in tmpl:
                    raise ValueError("Invalid template syntax")
                with sqlite3.connect(self.analytics_db) as conn:
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS generation_events (ts TEXT, objective TEXT, template TEXT)",
                    )
                    conn.execute(
                        "INSERT INTO generation_events (ts, objective, template) VALUES (?,?,?)",
                        (start.isoformat(), str(objective), tmpl),
                    )
                return tmpl
        return ""

    # ------------------------------------------------------------------
    def regenerate_template(self) -> str:
        if not self._last_objective:
            return ""
        return self.generate_template(self._last_objective)

    # ------------------------------------------------------------------
    def get_cluster_representatives(self) -> List[str]:
        if not self.cluster_model:
            return []
        corpus = self.templates + self.patterns
        vectorizer = TfidfVectorizer().fit(corpus)
        matrix = vectorizer.transform(corpus)
        reps: List[str] = []
        for idx in tqdm(
            range(self.cluster_model.n_clusters), desc="[PROGRESS] reps", unit="cluster"
        ):
            indices = [
                i for i, label in enumerate(self.cluster_model.labels_) if label == idx
            ]
            if not indices:
                continue
            sub_matrix = matrix[indices]
            centroid = self.cluster_model.cluster_centers_[idx].reshape(1, -1)
            sims = cosine_similarity(sub_matrix, centroid).ravel()
            best_local = indices[int(max(range(len(sims)), key=lambda i: sims[i]))]
            reps.append(corpus[best_local])
        return reps


__all__ = [
    "TemplateAutoGenerator",
    "DEFAULT_ANALYTICS_DB",
    "DEFAULT_COMPLETION_DB",
]
