#!/usr/bin/env python3
"""Database-driven documentation renderer with compliance checks."""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from template_engine.auto_generator import TemplateAutoGenerator, calculate_etc
from utils.log_utils import DEFAULT_ANALYTICS_DB, _log_event

RENDER_LOG_DIR = Path("artifacts/logs/template_rendering")
LOG_FILE = RENDER_LOG_DIR / "documentation_render.log"
ANALYTICS_DB = DEFAULT_ANALYTICS_DB

logger = logging.getLogger(__name__)


@dataclass
class DocumentationManager:
    """Render compliant documentation from the database."""

    database: Path = Path("databases") / "production.db"
    documentation_db: Path = Path("databases") / "documentation.db"
    analytics_db: Path = ANALYTICS_DB
    completion_db: Path = Path("databases/template_completion.db")
    dashboard_dir: Path = Path("dashboard/compliance")

    generator: TemplateAutoGenerator | None = None

    def _select_template_from_documentation_db(self, title: str) -> str:
        """Return template from documentation.db matching ``title``."""
        query = (
            "SELECT template_content FROM documentation_templates WHERE template_name = ? OR template_type = ? LIMIT 1"
        )
        try:
            with sqlite3.connect(self.documentation_db) as conn:
                cur = conn.execute(query, (title, title))
                row = cur.fetchone()
                if row:
                    return row[0]
        except sqlite3.Error as exc:
            logger.warning("doc template lookup failed: %s", exc)
        return ""

    def _select_template_from_db(self, title: str) -> str:
        """Return template from documentation or production databases."""
        doc_template = self._select_template_from_documentation_db(title)
        if doc_template:
            return doc_template

        query = (
            "SELECT template_content FROM template_repository "
            "WHERE template_name = ? OR template_category = ? "
            "ORDER BY success_rate DESC LIMIT 1"
        )
        try:
            with sqlite3.connect(self.database) as conn:
                cur = conn.execute(query, (title, title))
                row = cur.fetchone()
                if row:
                    return row[0]
        except sqlite3.Error as exc:
            logger.warning("template lookup failed: %s", exc)
        return ""

    def __post_init__(self) -> None:
        if self.generator is None:
            self.generator = TemplateAutoGenerator(
                analytics_db=self.analytics_db,
                completion_db=self.completion_db,
            )
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)

    def _update_dashboard(self, rendered: int) -> None:
        """Update dashboard/compliance metrics."""
        dashboard_file = self.dashboard_dir / "metrics.json"
        metrics = {
            "documentation_generated": rendered,
            "last_update": datetime.utcnow().isoformat(),
        }
        if dashboard_file.exists():
            try:
                data = json.loads(dashboard_file.read_text())
                if "metrics" in data:
                    metrics.update(data["metrics"])
            except json.JSONDecodeError:
                logger.warning("Invalid dashboard metrics file: %s", dashboard_file)
        metrics["documentation_generated"] = metrics.get("documentation_generated", 0) + rendered
        dashboard_file.write_text(
            json.dumps({"metrics": metrics, "status": "updated", "timestamp": metrics["last_update"]}, indent=2),
            encoding="utf-8",
        )

    def _refresh_rows(self) -> list[tuple[str, str, int]]:
        try:
            with sqlite3.connect(self.database) as conn:
                return conn.execute("SELECT title, content, compliance_score FROM documentation").fetchall()
        except sqlite3.Error as exc:
            logger.warning("Failed to read documentation table: %s", exc)
            return []

    def render(self) -> int:
        start_ts = time.time()
        if not self.database.exists():
            logger.error("Database not found: %s", self.database)
            return 0
        rows = self._refresh_rows()
        RENDER_LOG_DIR.mkdir(parents=True, exist_ok=True)
        count = 0
        for idx, (title, content, score) in enumerate(tqdm(rows, desc="render", unit="doc", leave=False), 1):
            if score < 60:
                continue
            template = self._select_template_from_db(title)
            if not template:
                template = self.generator.select_best_template(title)
            final_content = template or content
            (RENDER_LOG_DIR / f"{title}.md").write_text(final_content)
            (RENDER_LOG_DIR / f"{title}.html").write_text(f"<html><body><pre>{final_content}</pre></body></html>")
            (RENDER_LOG_DIR / f"{title}.json").write_text(
                json.dumps({"title": title, "content": final_content}, indent=2)
            )
            _log_event(
                {"event": "render", "title": title},
                table="render_events",
                db_path=self.analytics_db,
                test_mode=False,
            )
            with open(LOG_FILE, "a", encoding="utf-8") as logf:
                logf.write(f"{datetime.utcnow().isoformat()}|render|{title}\n")
            tqdm.write(f"ETC: {calculate_etc(start_ts, idx, len(rows))}")
            count += 1
        logger.info(
            "Rendered %s documents | ETC: %s",
            count,
            calculate_etc(start_ts, len(rows), len(rows)),
        )
        self._update_dashboard(count)
        return count


# Keep reference to the original class so tests that temporarily replace
# ``DocumentationManager`` do not leak those changes to subsequent tests.
_ORIGINAL_DOCUMENTATION_MANAGER = DocumentationManager


def dual_validate() -> bool:
    cls = DocumentationManager
    try:
        manager = cls()
        processed = manager.render()
        return processed > 0
    finally:
        # Restore the original class to avoid cross-test contamination when
        # ``DocumentationManager`` is patched in a test.
        globals()["DocumentationManager"] = _ORIGINAL_DOCUMENTATION_MANAGER


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = dual_validate()
    sys.exit(0 if success else 1)
