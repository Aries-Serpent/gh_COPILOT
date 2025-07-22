"""Objective similarity scoring utilities.

Each function follows the database-first pattern by reading templates from
``production.db`` before computing similarity scores. All scoring events are
recorded in ``analytics.db``. Visual progress indicators are provided via
``tqdm`` and a simple dual-copilot validation hook verifies that records were
written successfully.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


def _fetch_templates(production_db: Path) -> List[str]:
    """Return template text from ``production_db``."""
    if not production_db.exists():
        return []
    with sqlite3.connect(production_db) as conn:
        try:
            cur = conn.execute("SELECT template_code FROM code_templates")
            return [row[0] for row in cur.fetchall()]
        except sqlite3.Error:
            return []


def _log_scores(
    analytics_db: Path, objective: str, scores: Iterable[Tuple[int, float]]
) -> None:
    """Store similarity scores in ``analytics_db``."""
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS objective_similarity_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                objective TEXT,
                template_index INTEGER,
                score REAL,
                timestamp TEXT
            )"""
        )
        insert_sql = (
            "INSERT INTO objective_similarity_scores ("
            "objective, template_index, score, timestamp"
            ") VALUES (?, ?, ?, ?)"
        )
        for idx, score in scores:
            conn.execute(
                insert_sql,
                (objective, idx, float(score), datetime.utcnow().isoformat()),
            )
        conn.commit()


def score_objective_similarity(
    objective: str,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> List[Tuple[int, float]]:
    """Return similarity scores against templates in ``production_db``."""

    templates = _fetch_templates(production_db)
    if not templates:
        return []

    corpus = [objective] + templates
    vec = TfidfVectorizer().fit_transform(corpus)
    target_vec = vec[0]
    template_vecs = vec[1:]

    scores: List[Tuple[int, float]] = []
    with tqdm(total=len(templates), desc="Scoring", unit="tmpl") as bar:
        for idx in range(len(templates)):
            sim = cosine_similarity(target_vec, template_vecs[idx])[0][0]
            scores.append((idx, float(sim)))
            bar.update(1)

    _log_scores(analytics_db, objective, scores)
    return scores


def validate_scores(
    objective: str, analytics_db: Path = DEFAULT_ANALYTICS_DB
) -> bool:
    """Dual-copilot validation that scores for ``objective`` were logged."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM objective_similarity_scores WHERE objective=?",
            (objective,),
        )
        return cur.fetchone()[0] > 0


__all__ = [
    "score_objective_similarity",
    "validate_scores",
    "DEFAULT_PRODUCTION_DB",
    "DEFAULT_ANALYTICS_DB",
]
