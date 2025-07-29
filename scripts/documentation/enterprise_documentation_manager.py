from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Iterable, List

from tqdm import tqdm

from template_engine.auto_generator import (
    DEFAULT_ANALYTICS_DB,
    DEFAULT_COMPLETION_DB,
    TemplateAutoGenerator,
)
from template_engine.template_synchronizer import _compliance_score
from utils.database_utils import get_validated_production_db_connection
from utils.log_utils import _log_event

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "progress": "[PROGRESS]",
    "info": "[INFO]",
}


class EnterpriseDocumentationManager:
    """Generate documentation files from ``documentation.db``."""

    def __init__(
        self,
        workspace: Path | None = None,
        db_path: Path | None = None,
        analytics_db: Path = DEFAULT_ANALYTICS_DB,
        completion_db: Path = DEFAULT_COMPLETION_DB,
    ) -> None:
        self.workspace = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
        self.db_path = Path(
            db_path
            or os.getenv(
                "DOCUMENTATION_DB_PATH",
                self.workspace / "archives" / "documentation.db",
            )
        )
        self.output_dir = self.workspace / "documentation" / "generated" / "enterprise_docs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.generator = TemplateAutoGenerator(analytics_db, completion_db)

    # ------------------------------------------------------------------
    def query_documentation(self, doc_type: str) -> list[tuple[str, str]]:
        """Return ``doc_id`` and ``content`` for the given ``doc_type``."""
        if not self.db_path.exists():
            self.logger.error(f"{TEXT_INDICATORS['error']} Missing database {self.db_path}")
            return []
        query = "SELECT doc_id, content FROM enterprise_documentation WHERE doc_type=?"
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(query, (doc_type,)).fetchall()

    # ------------------------------------------------------------------
    def select_template(self, doc_type: str) -> str:
        """Return best template for ``doc_type`` using ``TemplateAutoGenerator``."""
        template = self.generator.select_best_template(doc_type)
        if not template:
            self.logger.info(f"{TEXT_INDICATORS['info']} No template found for {doc_type}")
        return template

    # ------------------------------------------------------------------
    def calculate_compliance(self, content: str) -> float:
        """Return compliance score using analytics rules."""
        score = _compliance_score(content)
        self.logger.info(f"{TEXT_INDICATORS['info']} Compliance score {score:.2f}")
        return score

    # ------------------------------------------------------------------
    def generate_files(self, doc_type: str) -> List[Path]:
        """Generate documentation files for ``doc_type``."""
        docs = self.query_documentation(doc_type)
        if not docs:
            return []
        template = self.select_template(doc_type)
        generated: List[Path] = []
        self.logger.info(f"{TEXT_INDICATORS['start']} Generating {doc_type} documentation")
        # record generation details in production.db
        with get_validated_production_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documentation_status (
                    doc_id TEXT PRIMARY KEY,
                    path TEXT,
                    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            with tqdm(total=len(docs), desc=f"{TEXT_INDICATORS['progress']} docs", unit="doc") as bar:
                for doc_id, content in docs:
                    text = template.replace("{content}", content) if template else content
                    score = self.calculate_compliance(text)
                    _log_event(
                        {
                            "event": "doc_generated",
                            "doc_id": doc_id,
                            "compliance_score": score,
                        },
                        table="correction_logs",
                        db_path=self.generator.analytics_db,
                    )
                    if score < 60.0:
                        self.logger.info(
                            f"{TEXT_INDICATORS['info']} Skipping {doc_id} due to low score {score:.2f}"
                        )
                        bar.update(1)
                        continue
                    path = self.output_dir / f"{doc_id}.md"
                    path.write_text(text)
                    generated.append(path)
                    cur.execute(
                        """
                        INSERT INTO documentation_status (doc_id, path, generated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(doc_id) DO UPDATE SET
                            path=excluded.path,
                            generated_at=excluded.generated_at
                        """,
                        (doc_id, str(path)),
                    )
                    bar.update(1)
            conn.commit()
        self.logger.info(f"{TEXT_INDICATORS['success']} Generated {len(generated)} {doc_type} files")
        return generated


__all__ = ["EnterpriseDocumentationManager"]
