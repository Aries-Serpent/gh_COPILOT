from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List

DEFAULT_ANALYTICS_DB = Path("analytics.db")
DEFAULT_COMPLETION_DB = Path("template_completion.db")


class DummyCluster:
    def __init__(self, size: int) -> None:
        self.n_clusters = size
        self.labels_ = list(range(size))


class TemplateAutoGenerator:
    """Minimal template generator used for tests."""

    def __init__(self, analytics_db: Path, completion_db: Path) -> None:
        self.analytics_db = Path(analytics_db)
        self.completion_db = Path(completion_db)
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.cluster_model = DummyCluster(len(self.patterns)) if self.patterns else DummyCluster(0)
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
                self._last_template = text
                return text
        self._last_template = ""
        return ""

    def regenerate_template(self) -> str:
        return self._last_template or ""
