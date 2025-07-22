from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


def compute_similarity_scores(
    objective: str,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> List[Tuple[int, float]]:
    """Compute similarity scores between the objective and templates."""
    templates: List[Tuple[int, str]] = []
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            try:
                cur = conn.execute("SELECT id, template_code FROM code_templates")
                templates = [(row[0], row[1]) for row in cur.fetchall()]
            except sqlite3.Error:
                templates = []

    if not templates:
        return []

    corpus = [objective] + [t[1] for t in templates]
    vectorizer = TfidfVectorizer().fit(corpus)
    obj_vec = vectorizer.transform([objective])

    scores: List[Tuple[int, float]] = []
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS objective_similarity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                objective TEXT,
                template_id INTEGER,
                score REAL,
                ts TEXT
            )"""
        )
        for tid, text in tqdm(templates, desc="Scoring", unit="tmpl"):
            vec = vectorizer.transform([text])
            score = float(cosine_similarity(obj_vec, vec)[0][0])
            scores.append((tid, score))
            conn.execute(
                "INSERT INTO objective_similarity (objective, template_id, score, ts) VALUES (?, ?, ?, ?)",
                (objective, tid, score, datetime.utcnow().isoformat()),
            )
        conn.commit()
    return scores


def validate_scores(
    objective: str,
    expected_count: int,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> bool:
    """DUAL COPILOT validation for similarity scoring."""
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM objective_similarity WHERE objective = ?",
            (objective,),
        )
        count = cur.fetchone()[0]
    return count >= expected_count

__all__ = ["compute_similarity_scores", "validate_scores"]
