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
import time

from template_engine.auto_generator import calculate_etc

from tqdm import tqdm

RENDER_LOG_DIR = Path("logs/template_rendering")
ANALYTICS_DB = Path("databases") / "analytics.db"

logger = logging.getLogger(__name__)


@dataclass
class DocumentationManager:
    """Render compliant documentation from the database."""

    database: Path = Path("production.db")

    def render(self) -> int:
        if not self.database.exists():
            logger.error("Database not found: %s", self.database)
            return 0
        start_ts = time.time()
        with sqlite3.connect(self.database) as conn:
            rows = conn.execute(
                "SELECT title, content, compliance_score FROM documentation"
            ).fetchall()
        RENDER_LOG_DIR.mkdir(parents=True, exist_ok=True)
        count = 0
        for idx, (title, content, score) in enumerate(tqdm(rows, desc="render", unit="doc", leave=False), 1):
            if score < 60:
                continue
            (RENDER_LOG_DIR / f"{title}.md").write_text(content)
            (RENDER_LOG_DIR / f"{title}.html").write_text(
                f"<html><body><pre>{content}</pre></body></html>"
            )
            (RENDER_LOG_DIR / f"{title}.json").write_text(
                json.dumps({"title": title, "content": content}, indent=2)
            )
            self._log_event("render", title)
            etc = calculate_etc(start_ts, idx, len(rows))
            tqdm.write(f"ETC: {etc}")
            count += 1
        return count

    def _log_event(self, action: str, title: str) -> None:
        try:
            with sqlite3.connect(ANALYTICS_DB) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS render_events (timestamp TEXT, action TEXT, title TEXT)"
                )
                conn.execute(
                    "INSERT INTO render_events (timestamp, action, title) VALUES (?, ?, ?)",
                    (datetime.utcnow().isoformat(), action, title),
                )
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

