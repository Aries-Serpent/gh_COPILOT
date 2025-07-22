from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

DEFAULT_DOC_DBS = [
    Path("databases/documentation.db"),
    Path("databases/template_documentation.db"),
]
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOG_DIR = Path("logs/template_rendering")


def _analyze_db(db: Path) -> Dict[str, int]:
    if not db.exists():
        return {"entries": 0}
    with sqlite3.connect(db) as conn:
        try:
            cur = conn.execute("SELECT COUNT(*) FROM documentation")
            count = cur.fetchone()[0]
        except sqlite3.Error:
            count = 0
    return {"entries": count}


def _log_summary(summary: Dict[str, Dict[str, int]], analytics_db: Path) -> None:
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS documentation_gap_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT,
                timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO documentation_gap_summary (summary, timestamp) VALUES (?, ?)",
            (json.dumps(summary), datetime.utcnow().isoformat()),
        )
        conn.commit()


def analyze_documentation(
    doc_dbs: List[Path] | None = None,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> Dict[str, Dict[str, int]]:
    paths = doc_dbs or DEFAULT_DOC_DBS
    summary: Dict[str, Dict[str, int]] = {}
    with tqdm(paths, desc="Analyzing", unit="db") as bar:
        for db in bar:
            summary[db.name] = _analyze_db(db)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"doc_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _log_summary(summary, analytics_db)
    return summary


def validate_analysis(analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM documentation_gap_summary")
        return cur.fetchone()[0] > 0
