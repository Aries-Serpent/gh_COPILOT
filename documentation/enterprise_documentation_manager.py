from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from tqdm import tqdm

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
}

logger = logging.getLogger(__name__)


class EnterpriseDocumentationManager:
    """Manage documentation generation using stored templates."""

    def __init__(self, doc_db: Path, analytics_db: Path) -> None:
        self.doc_db = Path(doc_db)
        self.analytics_db = Path(analytics_db)

    def query_documentation_database(self, doc_type: str) -> list[tuple]:
        with sqlite3.connect(self.doc_db) as conn:
            cur = conn.execute(
                "SELECT doc_id, doc_type, title, content FROM enterprise_documentation WHERE doc_type=?",
                (doc_type,),
            )
            return cur.fetchall()

    def discover_templates(self, doc_type: str) -> list[str]:
        with sqlite3.connect(self.doc_db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS documentation_templates (doc_type TEXT, template_content TEXT)"
            )
            cur = conn.execute(
                "SELECT template_content FROM documentation_templates WHERE doc_type=?",
                (doc_type,),
            )
            return [row[0] for row in cur.fetchall()]

    def select_optimal_template(self, templates: Iterable[str], existing_docs: list[tuple]) -> str:
        for tmpl in templates:
            if tmpl:
                return tmpl
        return ""

    def apply_template_intelligence(self, templates: Iterable[str], docs: list[tuple]) -> str:
        tmpl = self.select_optimal_template(list(templates), docs)
        return tmpl.format(count=len(docs)) if "{count}" in tmpl else tmpl

    def calculate_compliance(self, content: str) -> float:
        return min(1.0, max(0.0, 1 - len(content) / 1000))

    def store_documentation(self, content: str, compliance_score: float) -> None:
        with sqlite3.connect(self.doc_db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS enterprise_documentation (doc_id INTEGER PRIMARY KEY AUTOINCREMENT, doc_type TEXT, title TEXT, content TEXT, compliance REAL)"
            )
            with tqdm(total=1, desc=f"{TEXT_INDICATORS['info']} store") as bar:
                conn.execute(
                    "INSERT INTO enterprise_documentation (doc_type, title, content, compliance) VALUES (?, ?, ?, ?)",
                    ("AUTO", "Generated", content, compliance_score),
                )
                conn.commit()
                bar.update(1)
        with sqlite3.connect(self.analytics_db) as log_conn:
            log_conn.execute(
                "CREATE TABLE IF NOT EXISTS generation_events (timestamp TEXT, compliance REAL)"
            )
            log_conn.execute(
                "INSERT INTO generation_events VALUES (?, ?)",
                (datetime.now().isoformat(), compliance_score),
            )
            log_conn.commit()
        logger.info(
            f"{TEXT_INDICATORS['success']} Stored documentation with compliance {compliance_score:.2f}"
        )
