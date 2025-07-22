from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


def _fetch_templates(production_db: Path) -> List[Tuple[str, str]]:
    if not production_db.exists():
        return []
    with sqlite3.connect(production_db) as conn:
        try:
            cur = conn.execute(
                "SELECT template_name, template_content FROM templates"
            )
            return [(row[0], row[1]) for row in cur.fetchall()]
        except sqlite3.Error:
            return []


def _similarity(obj: str, content: str) -> float:
    obj_words = set(re.findall(r"\w+", obj.lower()))
    content_words = set(re.findall(r"\w+", content.lower()))
    if not obj_words or not content_words:
        return 0.0
    common = obj_words.intersection(content_words)
    return len(common) / len(obj_words)


def _log_score(analytics_db: Path, objective: str, template: str, score: float) -> None:
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS objective_similarity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                objective TEXT,
                template_name TEXT,
                similarity REAL,
                timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO objective_similarity_logs (objective, template_name, similarity, timestamp) VALUES (?, ?, ?, ?)",
            (objective, template, score, datetime.utcnow().isoformat()),
        )
        conn.commit()


def score_objective(
    objective: str,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> Tuple[str, float]:
    templates = _fetch_templates(production_db)
    best_template = ""
    best_score = 0.0
    with tqdm(templates, desc="Scoring", unit="tmpl") as bar:
        for name, content in bar:
            score = _similarity(objective, content)
            if score > best_score:
                best_score = score
                best_template = name
    _log_score(analytics_db, objective, best_template, best_score)
    return best_template, best_score


def validate_similarity(objective: str, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM objective_similarity_logs WHERE objective = ?",
            (objective,),
        )
        return cur.fetchone()[0] > 0
