"""Documentation database gap analyzer.

This refactored utility scans documentation databases for missing content and
records a summary to ``logs/template_rendering`` and ``analytics.db``. The
implementation follows the database-first pattern with progress indicators and a
simple validation step.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

from tqdm import tqdm


LOG_DIR = Path(os.getenv("GH_COPILOT_WORKSPACE", ".")) / "logs" / "template_rendering"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"doc_gap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

ANALYTICS_DB = Path("databases/analytics.db")
DOC_DBS = [
    Path("databases/documentation.db"),
    Path("databases/template_documentation.db"),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)


class DocumentationDBAnalyzer:
    """Analyze documentation databases for missing entries."""

    def __init__(self, doc_dbs: List[Path] | None = None) -> None:
        self.doc_dbs = doc_dbs or DOC_DBS

    # ------------------------------------------------------------------
    def analyze(self) -> dict:
        """Scan documentation databases for gaps."""
        summary: dict[str, int] = {}
        total_entries = 0
        for db in self.doc_dbs:
            if not db.exists():
                continue
            with sqlite3.connect(db) as conn:
                cur = conn.execute(
                    "SELECT doc_type, COUNT(content) FROM enterprise_documentation"
                    " GROUP BY doc_type"
                )
                rows = cur.fetchall()
            with tqdm(rows, desc=f"Scanning {db.name}", unit="type") as bar:
                for doc_type, count in rows:
                    summary[doc_type] = summary.get(doc_type, 0) + count
                    total_entries += count
                    bar.update(1)
        summary["total"] = total_entries
        self._log_summary(summary)
        self._record_summary(summary)
        return summary

    # ------------------------------------------------------------------
    def _log_summary(self, summary: dict) -> None:
        LOG_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        logging.info("Documentation gap summary written to log file")

    # ------------------------------------------------------------------
    def _record_summary(self, summary: dict) -> None:
        ANALYTICS_DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS documentation_gap_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary TEXT,
                    timestamp TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO documentation_gap_analysis (summary, timestamp) VALUES (?, ?)",
                (json.dumps(summary), datetime.utcnow().isoformat()),
            )
            conn.commit()

    # ------------------------------------------------------------------
    def validate(self, expected_total: int) -> bool:
        """Check that at least ``expected_total`` entries were recorded."""
        if not ANALYTICS_DB.exists():
            return False
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT summary FROM documentation_gap_analysis ORDER BY id DESC LIMIT 1"
            )
            row = cur.fetchone()
            if not row:
                return False
            data = json.loads(row[0])
            return data.get("total", 0) >= expected_total


def main() -> None:
    analyzer = DocumentationDBAnalyzer()
    summary = analyzer.analyze()
    valid = analyzer.validate(summary.get("total", 0))
    if valid:
        logging.info("Documentation analysis validated successfully")
    else:
        logging.error("Documentation analysis validation failed")


if __name__ == "__main__":
    main()

