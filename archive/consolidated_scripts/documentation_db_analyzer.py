from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterable

from tqdm import tqdm

DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
DEFAULT_DOC_DBS = [
    Path("databases/documentation.db"),
    Path("databases/documentation_templates.db"),
]
LOG_DIR = Path("logs/template_rendering")


class DocumentationDBAnalyzer:
    """Scan documentation databases for gaps and log summaries."""

    def __init__(self, doc_dbs: Iterable[Path] | None = None, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> None:
        self.doc_dbs = list(doc_dbs) if doc_dbs else DEFAULT_DOC_DBS
        self.analytics_db = analytics_db
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_file = LOG_DIR / f"doc_db_analyzer_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"

    def scan(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {"timestamp": datetime.utcnow().isoformat(), "databases": {}}
        for db in tqdm(self.doc_dbs, desc="Scanning", unit="db"):
            if not db.exists():
                continue
            with sqlite3.connect(db) as conn:
                cur = conn.execute(
                    "SELECT doc_type, COUNT(*) FROM enterprise_documentation GROUP BY doc_type"
                )
                rows = cur.fetchall()
            summary["databases"][str(db)] = {dt: cnt for dt, cnt in rows}
        self._write_log(summary)
        self._log_to_db(summary)
        return summary

    def _write_log(self, summary: Dict[str, Any]) -> None:
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary) + "\n")

    def _log_to_db(self, summary: Dict[str, Any]) -> None:
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS documentation_gap_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    details TEXT,
                    ts TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO documentation_gap_analysis (details, ts) VALUES (?, ?)",
                (json.dumps(summary), summary["timestamp"]),
            )
            conn.commit()

    def validate(self) -> bool:
        with sqlite3.connect(self.analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM documentation_gap_analysis")
            return cur.fetchone()[0] > 0


__all__ = ["DocumentationDBAnalyzer"]
