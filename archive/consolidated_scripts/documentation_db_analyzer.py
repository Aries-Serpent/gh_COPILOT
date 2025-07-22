from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Union

from tqdm import tqdm

DEFAULT_DOC_DBS = [
    Path("databases/documentation.db"),
    Path("databases/documentation_templates.db"),
]
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOG_DIR = Path("logs/template_rendering")


def analyze_documentation_gaps(
    doc_dbs: Iterable[Path] = DEFAULT_DOC_DBS,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
    log_dir: Path = LOG_DIR,
) -> List[Dict[str, Union[str, int]]]:
    """Scan documentation databases for missing content and log summaries."""
    results: List[Dict[str, Union[str, int]]] = []
    timestamp = datetime.utcnow().isoformat()
    for db_path in doc_dbs:
        gaps = 0
        if db_path.exists():
            with sqlite3.connect(db_path) as conn:
                try:
                    rows = conn.execute("SELECT title, content FROM documentation")
                    data = rows.fetchall()
                except sqlite3.Error:
                    data = []
            for title, content in tqdm(data, desc=f"{db_path.name}", unit="doc"):
                if not content:
                    gaps += 1
        results.append({"database": db_path.name, "gaps": gaps})
    log_dir.mkdir(parents=True, exist_ok=True)
    summary = {"timestamp": timestamp, "results": results}
    out_file = (
        log_dir
        / f"documentation_gap_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS documentation_gap_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                database TEXT,
                gaps INTEGER,
                timestamp TEXT
            )"""
        )
        for item in results:
            conn.execute(
                "INSERT INTO documentation_gap_analysis (database, gaps, timestamp) VALUES (?, ?, ?)",
                (item["database"], item["gaps"], timestamp),
            )
        conn.commit()
    return results


def validate_analysis(analytics_db: Path, expected: int) -> bool:
    """Validate the number of gap analysis records."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM documentation_gap_analysis")
        count = cur.fetchone()[0]
    return count >= expected
