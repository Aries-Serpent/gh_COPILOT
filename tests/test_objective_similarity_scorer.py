import os
import sqlite3
from pathlib import Path

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from template_engine.objective_similarity_scorer import (
    score_objective_similarity,
    validate_scores,
)


def test_score_objective_similarity(tmp_path: Path) -> None:
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute(
            "INSERT INTO code_templates (template_code) VALUES ('print(\"hello\")')"
        )

    scores = score_objective_similarity("hello world", prod, analytics)
    assert scores
    assert validate_scores("hello world", analytics)

