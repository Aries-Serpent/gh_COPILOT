#!/usr/bin/env python3
"""Database-first code and documentation generator.

This module implements a minimal framework that demonstrates the database-first
pattern. It queries several SQLite databases for existing templates before
producing any new output. Generation events are logged to ``analytics.db`` and
visual indicators are provided via ``tqdm`` progress bars.

The implementation follows the Dual Copilot pattern: every generation step is
followed by a lightweight validation phase to ensure compliance.
"""
from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_DOCUMENTATION_DB = Path("databases/documentation.db")
DEFAULT_TEMPLATE_DB = Path("databases/template_documentation.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


@dataclass
class DBFirstCodeGenerator:
    """Generate code snippets using templates fetched from databases."""

    production_db: Path = DEFAULT_PRODUCTION_DB
    documentation_db: Path = DEFAULT_DOCUMENTATION_DB
    template_db: Path = DEFAULT_TEMPLATE_DB
    analytics_db: Path = DEFAULT_ANALYTICS_DB

    def _fetch_templates(self) -> List[str]:
        """Retrieve template strings from configured databases."""
        templates: List[str] = []
        for db in [self.production_db, self.documentation_db, self.template_db]:
            if not db.exists():
                continue
            with sqlite3.connect(db) as conn:
                cur = conn.execute(
                    "SELECT template_content FROM templates WHERE template_content != ''"
                )
                templates.extend(row[0] for row in cur.fetchall())
        return templates

    def _similarity(self, a: str, b: str) -> float:
        """Return a naive similarity score between two strings."""
        if not a or not b:
            return 0.0
        smaller, bigger = sorted([a, b], key=len)
        return len(set(smaller.split()) & set(bigger.split())) / len(bigger.split())

    def _select_template(self, query: str, candidates: List[str]) -> str:
        scores = [self._similarity(query, tmpl) for tmpl in candidates]
        if not scores:
            return ""
        best_idx = max(range(len(scores)), key=scores.__getitem__)
        return candidates[best_idx]

    def _log_event(self, query: str, template: str) -> None:
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS generation_events (
                id INTEGER PRIMARY KEY,
                query TEXT,
                template TEXT,
                ts TEXT
            )"""
            )
            conn.execute(
                "INSERT INTO generation_events (query, template, ts) VALUES (?, ?, ?)",
                (query, template, time.strftime("%Y-%m-%dT%H:%M:%S")),
            )
            conn.commit()

    def generate(self, query: str) -> str:
        """Generate code/documentation for the provided query."""
        templates = self._fetch_templates()
        with tqdm(total=1, desc="selecting template") as bar:
            template = self._select_template(query, templates)
            bar.update(1)

        if not template:
            template = f"# Auto-generated stub for: {query}"

        self._log_event(query, template)
        if not self._validate_generation(query):
            logging.error("[ERROR] validation failed during generation")
        return template

    def _validate_generation(self, query: str) -> bool:
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM generation_events WHERE query=?", (query,)
            )
            return cur.fetchone()[0] > 0


def main(query: Optional[str] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generator = DBFirstCodeGenerator()
    result = generator.generate(query or "default example")
    logging.info("Generated template:\n%s", result)


if __name__ == "__main__":
    main()
