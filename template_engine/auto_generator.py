#!/usr/bin/env python3
"""Simplified template generation engine."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("template_completion.db")


@dataclass
class DummyClusterModel:
    n_clusters: int


class TemplateAutoGenerator:
    """Generate templates using simple rules."""

    def __init__(self, analytics_db: Path, completion_db: Path) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.cluster_model = DummyClusterModel(max(1, len(self.templates)))
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
        count = self.cluster_model.n_clusters
        reps = self.templates[:count]
        if len(reps) < count:
            reps.extend(self.patterns[: count - len(reps)])
        return reps

    def objective_similarity(self, a: str, b: str) -> float:
        return 1.0 if a == b else 0.0

    def select_best_template(self, target: str) -> str:
        return target
