"""Pipeline for automated template curation.

This module combines asset ingestion, pattern mining, template
deduplication, and objective similarity scoring. Results are recorded
in ``analytics.db`` for downstream use.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

from .pattern_mining_engine import (
    DEFAULT_ANALYTICS_DB,
    DEFAULT_PRODUCTION_DB,
    ingest_assets,
    mine_patterns,
)
from .template_synchronizer import _cluster_templates
from .objective_similarity_scorer import compute_similarity_scores


def _load_templates_from_dir(tmpl_dir: Path, production_db: Path) -> None:
    """Load template files into ``production_db`` tables."""
    production_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(production_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS code_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_code TEXT
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS templates (
                name TEXT,
                template_content TEXT
            )"""
        )
        for path in tmpl_dir.rglob("*"):
            if path.is_file():
                text = path.read_text()
                conn.execute(
                    "INSERT INTO code_templates (template_code) VALUES (?)",
                    (text,),
                )
                conn.execute(
                    "INSERT INTO templates (name, template_content) VALUES (?, ?)",
                    (path.stem, text),
                )
        conn.commit()


def curate_templates(
    doc_dir: Path,
    tmpl_dir: Path,
    objective: str,
    *,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> Dict[str, object]:
    """Run ingestion, mining, deduplication and scoring.

    Returns a summary mapping with discovered patterns, the number of
    clusters after deduplication, and similarity scores for the provided
    ``objective``.
    """

    ingest_assets(doc_dir, tmpl_dir, production_db=production_db, analytics_db=analytics_db)
    _load_templates_from_dir(tmpl_dir, production_db)

    patterns = mine_patterns(production_db=production_db, analytics_db=analytics_db)

    templates: Dict[str, str] = {}
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            rows = conn.execute("SELECT name, template_content FROM templates").fetchall()
            templates = {name: content for name, content in rows}

    deduped = _cluster_templates(templates)

    scores = compute_similarity_scores(
        objective,
        production_db=production_db,
        analytics_db=analytics_db,
        methods=["tfidf", "jaccard"],
    )

    return {"patterns": patterns, "clusters": len(deduped), "scores": scores}


__all__ = ["curate_templates"]

