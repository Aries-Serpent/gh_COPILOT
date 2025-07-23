#!/usr/bin/env python3
"""Database-driven documentation renderer with compliance checks."""
from __future__ import annotations

import json
import logging
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from template_engine.auto_generator import TemplateAutoGenerator, calculate_etc

from tqdm import tqdm

RENDER_LOG_DIR = Path("logs/template_rendering")
LOG_FILE = RENDER_LOG_DIR / "documentation_render.log"
ANALYTICS_DB = Path("databases") / "analytics.db"

logger = logging.getLogger(__name__)


@dataclass
class DocumentationManager:
    """Render compliant documentation from the database."""

    database: Path = Path("production.db")
    analytics_db: Path = ANALYTICS_DB
    completion_db: Path = Path("databases/template_completion.db")

    generator: TemplateAutoGenerator | None = None

    def _refresh_rows(self) -> list[tuple[str, str, int]]:
        with sqlite3.connect(self.database) as conn:
            return conn.execute(
                "SELECT title, content, compliance_score FROM documentation"
            ).fetchall()

    def render(self) -> int:
        start_ts = time.time()
        if not self.database.exists():
            logger.error("Database not found: %s", self.database)
            return 0
        rows = self._refresh_rows()
        RENDER_LOG_DIR.mkdir(parents=True, exist_ok=True)
        generator = TemplateAutoGenerator(
            analytics_db=self.analytics_db, completion_db=self.completion_db
        )
        count = 0
        generator = TemplateAutoGenerator(self.analytics_db, self.completion_db)
        for idx, (title, content, score) in enumerate(
            tqdm(rows, desc="render", unit="doc", leave=False), 1
        ):
            if score < 60:
                continue
            template = self.generator.select_best_template(title)
            final_content = template or content
            (RENDER_LOG_DIR / f"{title}.md").write_text(final_content)
            (RENDER_LOG_DIR / f"{title}.html").write_text(
                f"<html><body><pre>{final_content}</pre></body></html>"
            )
            (RENDER_LOG_DIR / f"{title}.json").write_text(
                json.dumps({"title": title, "content": final_content}, indent=2)
            )
            self._log_event("render", title)
            tqdm.write(f"ETC: {calculate_etc(start_ts, idx, len(rows))}")
            count += 1
        logger.info(
            "Rendered %s documents | ETC: %s",
            count,
            calculate_etc(start_ts, len(rows), len(rows)),
        )
        return count

    def _log_event(self, action: str, title: str) -> None:
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS render_events (timestamp TEXT, action TEXT, title TEXT)"
                )
                conn.execute(
                    "INSERT INTO render_events (timestamp, action, title) VALUES (?, ?, ?)",
                    (datetime.utcnow().isoformat(), action, title),
                )
            with open(LOG_FILE, "a", encoding="utf-8") as logf:
                logf.write(f"{datetime.utcnow().isoformat()}|{action}|{title}\n")
        except sqlite3.Error as exc:
            logger.error("Failed to log render event: %s", exc)


def dual_validate() -> bool:
    manager = DocumentationManager()
    processed = manager.render()
    return processed > 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = dual_validate()
    sys.exit(0 if success else 1)

