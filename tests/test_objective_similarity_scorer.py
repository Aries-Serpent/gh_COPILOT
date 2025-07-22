import sqlite3
from pathlib import Path

from template_engine.objective_similarity_scorer import (
    compute_objective_similarity,
    validate_similarity,
)


def test_compute_objective_similarity(tmp_path: Path) -> None:
    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE objectives (name TEXT)")
        conn.executemany(
            "INSERT INTO objectives (name) VALUES (?)",
            [("alpha beta",), ("beta gamma",)],
        )
    analytics = tmp_path / "analytics.db"
    results = compute_objective_similarity(prod, analytics)
    assert results
    assert validate_similarity(analytics, len(results))
