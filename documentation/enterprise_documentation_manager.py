import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
ANALYTICS_DB = WORKSPACE_ROOT / "analytics.db"

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
}


class EnterpriseDocumentationManager:
    """Database-driven documentation manager."""

    def __init__(self, db_path: str = "production.db") -> None:
        self.db_path = WORKSPACE_ROOT / db_path if not Path(db_path).is_absolute() else Path(db_path)
        self.logger = logging.getLogger(__name__)

    def query_documentation_database(self, doc_type: str) -> List[Tuple[str, str]]:
        """Fetch documentation entries of a given type."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS enterprise_documentation (
                    doc_id TEXT,
                    doc_type TEXT,
                    title TEXT,
                    content TEXT
                )
                """
            )
            cur = conn.execute(
                "SELECT title, content FROM enterprise_documentation WHERE doc_type=?",
                (doc_type,),
            )
            rows = cur.fetchall()
        self.logger.info(f"{TEXT_INDICATORS['info']} {len(rows)} docs fetched")
        return rows

    def discover_templates(self, doc_type: str) -> List[Tuple[str, str]]:
        """Retrieve templates for a documentation type."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documentation_templates (
                    template_name TEXT,
                    template_content TEXT,
                    doc_type TEXT
                )
                """
            )
            cur = conn.execute(
                "SELECT template_name, template_content FROM documentation_templates WHERE doc_type=?",
                (doc_type,),
            )
            templates = cur.fetchall()
        self.logger.info(f"{TEXT_INDICATORS['info']} {len(templates)} templates discovered")
        return templates

    def select_optimal_template(
        self, templates: List[Tuple[str, str]], existing_docs: List[Tuple[str, str]]
    ) -> Tuple[str, str]:
        """Select the first available template."""
        if not templates:
            raise ValueError("No templates available")
        self.logger.info(f"{TEXT_INDICATORS['info']} Template selected {templates[0][0]}")
        return templates[0]

    def apply_template_intelligence(
        self, templates: List[Tuple[str, str]], existing_docs: List[Tuple[str, str]]
    ) -> str:
        """Render documentation content using templates."""
        rendered = []
        for name, content in tqdm(templates, desc="[PROGRESS] rendering", unit="template"):
            rendered.append(content.format(count=len(existing_docs)))
        combined = "\n".join(rendered)
        self.logger.info(f"{TEXT_INDICATORS['info']} Rendered {len(rendered)} templates")
        return combined

    def calculate_compliance(self, content: str) -> float:
        """Compute a simple compliance score."""
        score = len(content.strip()) / 100.0
        self.logger.info(f"{TEXT_INDICATORS['info']} Compliance score {score:.2f}")
        return score

    def store_documentation(self, content: str, compliance_score: float) -> None:
        """Persist generated documentation event to analytics.db."""
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documentation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    content_length INTEGER,
                    compliance REAL
                )
                """
            )
            conn.execute(
                "INSERT INTO documentation_events (timestamp, content_length, compliance) VALUES (?, ?, ?)",
                (datetime.now(), len(content), compliance_score),
            )
            conn.commit()
        self.logger.info(f"{TEXT_INDICATORS['success']} Documentation stored")

