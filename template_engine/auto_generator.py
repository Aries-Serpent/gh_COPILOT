from __future__ import annotations

import ast
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional

import numpy as np
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("databases/template_completion.db")


class TemplateAutoGenerator:
    """Generate templates from stored database patterns."""

    def __init__(self, analytics_db: Path | str, completion_db: Path | str) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns: List[str] = self._load_patterns()
        self.templates: List[str] = self._load_templates()
        self.cluster_model: Optional[KMeans] = self._cluster_patterns()
        self._last_template: str = ""

    # ------------------------------------------------------------------
    def _load_patterns(self) -> List[str]:
        query = "SELECT replacement_template FROM ml_pattern_optimization"
        if not self.analytics_db.exists():
            return []
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                rows = conn.execute(query).fetchall()
                return [r[0] for r in rows]
        except sqlite3.Error:
            return []

    def _load_templates(self) -> List[str]:
        query = "SELECT template_content FROM templates"
        if not self.completion_db.exists():
            return []
        try:
            with sqlite3.connect(self.completion_db) as conn:
                rows = conn.execute(query).fetchall()
                return [r[0] for r in rows]
        except sqlite3.Error:
            return []

    # ------------------------------------------------------------------
    def _cluster_patterns(self) -> Optional[KMeans]:
        if not self.patterns:
            return None
        data = np.array([[len(p)] for p in self.patterns])
        n_clusters = min(len(self.patterns), 2)
        model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
        model.fit(data)
        return model

    # ------------------------------------------------------------------
    def get_cluster_representatives(self) -> List[str]:
        if not self.cluster_model:
            return []
        reps: List[str] = []
        centers = self.cluster_model.cluster_centers_.ravel()
        for idx in range(self.cluster_model.n_clusters):
            indices = np.where(self.cluster_model.labels_ == idx)[0]
            if not indices.size:
                continue
            cluster_patterns = [self.patterns[i] for i in indices]
            rep = min(
                cluster_patterns,
                key=lambda p: abs(len(p) - centers[idx]),
            )
            reps.append(rep)
        return reps

    # ------------------------------------------------------------------
    def _format_candidate(self, candidate: str, replacements: dict) -> str:
        try:
            return candidate.format(**replacements)
        except Exception:
            return candidate

    def _is_valid_python(self, text: str) -> bool:
        try:
            ast.parse(text)
            return True
        except SyntaxError:
            return False

    # ------------------------------------------------------------------
    def generate_template(self, replacements: dict) -> str:
        search_terms = set(map(str, replacements.values()))
        candidates = self.patterns + self.templates
        match = next((p for p in candidates if any(t in p for t in search_terms)), None)
        if not match:
            return ""
        candidate = self._format_candidate(match, replacements)
        if not self._is_valid_python(candidate):
            raise ValueError("Generated template has invalid syntax")
        self._last_template = candidate
        return candidate

    # ------------------------------------------------------------------
    def regenerate_template(self) -> str:
        return self._last_template
