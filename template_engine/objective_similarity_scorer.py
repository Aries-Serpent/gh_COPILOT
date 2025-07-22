from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


def _jaccard(a: str, b: str) -> float:
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def compute_objective_similarity(
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> List[Tuple[str, str, float]]:
    """Compute pairwise similarity of objectives and log results."""
    objectives: List[str] = []
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            try:
                cur = conn.execute("SELECT name FROM objectives")
                objectives = [row[0] for row in cur.fetchall()]
            except sqlite3.Error:
                return []
    results: List[Tuple[str, str, float]] = []
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS objective_similarity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                objective_a TEXT,
                objective_b TEXT,
                score REAL,
                timestamp TEXT
            )"""
        )
        for i in tqdm(range(len(objectives)), desc="Scoring", unit="pair"):
            for j in range(i + 1, len(objectives)):
                score = _jaccard(objectives[i], objectives[j])
                conn.execute(
                    "INSERT INTO objective_similarity (objective_a, objective_b, score, timestamp) VALUES (?, ?, ?, ?)",
                    (
                        objectives[i],
                        objectives[j],
                        score,
                        datetime.utcnow().isoformat(),
                    ),
                )
                results.append((objectives[i], objectives[j], score))
        conn.commit()
    return results


def validate_similarity(analytics_db: Path, expected: int) -> bool:
    """Validate analytics records count."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM objective_similarity")
        count = cur.fetchone()[0]
    return count >= expected
