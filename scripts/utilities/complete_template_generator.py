#!/usr/bin/env python3
"""CompleteTemplateGenerator
===========================

Generate templates autonomously from database patterns using
``template_engine`` utilities. Each generated template is recorded in
``production.db`` for auditing.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

from tqdm import tqdm

from template_engine.auto_generator import (DEFAULT_ANALYTICS_DB,
                                            DEFAULT_COMPLETION_DB,
                                            TemplateAutoGenerator)

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "progress": "[PROGRESS]",
    "info": "[INFO]",
}

logger = logging.getLogger(__name__)


class CompleteTemplateGenerator:
    """Autonomously create and regenerate templates from stored patterns."""

    def __init__(
        self,
        analytics_db: Path = DEFAULT_ANALYTICS_DB,
        completion_db: Path = DEFAULT_COMPLETION_DB,
        production_db: Path = Path("production.db"),
    ) -> None:
        self.analytics_db = analytics_db
        self.completion_db = completion_db
        self.production_db = production_db
        self.generator = TemplateAutoGenerator(analytics_db, completion_db)
        self._ensure_stats_table()
        self._ensure_generated_table()

    # ------------------------------------------------------------------
    def _ensure_stats_table(self) -> None:
        """Create stats table if it does not exist."""
        with sqlite3.connect(self.production_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS template_generation_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cluster_id INTEGER NOT NULL,
                    template_length INTEGER NOT NULL,
                    generated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    def _ensure_generated_table(self) -> None:
        """Create generated templates table if needed."""
        with sqlite3.connect(self.production_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    template_content TEXT NOT NULL,
                    generated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    def _record_stats(self, cluster_id: int, template: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(self.production_db) as conn:
            conn.execute(
                "INSERT INTO template_generation_stats"
                " (cluster_id, template_length, generated_at) VALUES (?, ?, ?)",
                (cluster_id, len(template), timestamp),
            )
            conn.commit()

    # ------------------------------------------------------------------
    @staticmethod
    def _validate_template(text: str) -> bool:
        return len(text.strip()) >= 10

    # ------------------------------------------------------------------
    def create_templates(self) -> List[str]:
        """Synthesize new templates from known patterns."""
        templates: List[str] = []
        clusters = self.generator.cluster_model
        patterns = self.generator.patterns
        if not patterns or clusters is None:
            return templates

        with sqlite3.connect(self.production_db) as conn:
            data_to_insert = []
            generated_records = []
            with tqdm(total=clusters.n_clusters, \
                desc=f"{TEXT_INDICATORS['progress']} create") as bar:
                for cluster_id in range(clusters.n_clusters):
                    indices = [i for i, label in enumerate(clusters.labels_) if label == cluster_id]
                    if not indices:
                        bar.update(1)
                        continue
                    cluster_patterns = [patterns[i] for i in indices]
                    candidate = max(cluster_patterns, key=len)
                    if self._validate_template(candidate):
                        templates.append(candidate)
                        timestamp = datetime.utcnow().isoformat()
                        data_to_insert.append((cluster_id, len(candidate), timestamp))
                        template_id = f"cluster_{cluster_id}_{len(candidate)}"
                        generated_records.append((template_id, candidate, timestamp))
                    bar.update(1)
            if data_to_insert:
                conn.executemany(
                    "INSERT INTO template_generation_stats"
                    " (cluster_id, template_length, generated_at) VALUES (?, ?, ?)",
                    data_to_insert,
                )
            if generated_records:
                conn.executemany(
                    "INSERT INTO generated_templates"
                    " (template_id, template_content, generated_at) VALUES (?, ?, ?)",
                    generated_records,
                )
        return templates

    # ------------------------------------------------------------------
    def regenerate_templates(self) -> List[str]:
        """Reinitialize generator and regenerate templates."""
        logger.info(f"{TEXT_INDICATORS['info']} regenerating templates")
        self.generator = TemplateAutoGenerator(self.analytics_db, self.completion_db)
        return self.create_templates()


if __name__ == "__main__":  # pragma: no cover - manual execution
    logging.basicConfig(level=logging.INFO)
    gen = CompleteTemplateGenerator()
    for temp in gen.create_templates():
        print(temp)
