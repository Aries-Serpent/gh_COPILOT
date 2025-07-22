#!/usr/bin/env python3
"""Refactored documentation manager with database-first template lookup."""
from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tqdm import tqdm

DEFAULT_DOC_DB = Path("databases/documentation.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOG_DIR = Path("logs/template_rendering")


@dataclass
class EnterpriseDocumentationManager:
    doc_db: Path = DEFAULT_DOC_DB
    analytics_db: Path = DEFAULT_ANALYTICS_DB

    def render(self, key: str) -> str:
        templates = self._fetch_templates(key)
        with tqdm(total=1, desc="render", unit="doc") as bar:
            doc = templates[0] if templates else f"Documentation for {key}"
            bar.update(1)
        self._log_render(key, doc)
        return doc

    def _fetch_templates(self, key: str) -> list[str]:
        if not self.doc_db.exists():
            return []
        with sqlite3.connect(self.doc_db) as conn:
            cur = conn.execute(
                "SELECT doc_content FROM docs WHERE doc_key=?", (key,)
            )
            return [row[0] for row in cur.fetchall()]

    def _log_render(self, key: str, content: str) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS doc_renders (
                id INTEGER PRIMARY KEY,
                doc_key TEXT,
                ts TEXT
            )"""
            )
            conn.execute(
                "INSERT INTO doc_renders (doc_key, ts) VALUES (?, ?)",
                (key, time.strftime("%Y-%m-%dT%H:%M:%S")),
            )
            conn.commit()
        (LOG_DIR / f"{key}.md").write_text(content, encoding="utf-8")


def main(key: Optional[str] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    manager = EnterpriseDocumentationManager()
    result = manager.render(key or "intro")
    logging.info("Rendered documentation:\n%s", result)


if __name__ == "__main__":
    main()
