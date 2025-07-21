#!/usr/bin/env python3
"""Template Matcher using clustering algorithms.

This script reads text from STDIN, loads code templates from the
``production.db`` database, and uses a KMeans-based clustering
algorithm to identify the best matching template.
"""

from __future__ import annotations

import sys
import sqlite3
from pathlib import Path
from typing import List

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = Path("databases/production.db")


def load_templates() -> List[str]:
    """Load templates from the production database."""
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT template_code FROM code_templates WHERE template_code != ''"
        ).fetchall()
    return [row[0] for row in rows]


def find_best_template(input_text: str, templates: List[str]) -> str:
    """Return the template most similar to ``input_text``."""
    if not templates:
        return ""

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(templates)

    # Auto-select cluster count using a simple heuristic
    n_clusters = min(len(templates), max(2, len(templates) // 3))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    input_vec = vectorizer.transform([input_text])
    cluster = kmeans.predict(input_vec)[0]

    candidates = [tmpl for tmpl, lbl in zip(templates, labels) if lbl == cluster]
    if not candidates:
        return ""

    candidate_vecs = vectorizer.transform(candidates)
    sims = cosine_similarity(input_vec, candidate_vecs)[0]
    best_index = sims.argmax()
    return candidates[best_index]


def main() -> int:
    text = sys.stdin.read()
    if not text.strip():
        print("", end="")
        return 0

    templates = load_templates()
    best = find_best_template(text, templates)
    if best:
        print(best)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
