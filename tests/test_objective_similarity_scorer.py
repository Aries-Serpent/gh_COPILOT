import os
import sqlite3
from pathlib import Path

from datetime import datetime
from template_engine.objective_similarity_scorer import (
    compute_similarity_scores,
    validate_scores,
)

def test_compute_similarity_scores(tmp_path: Path) -> None:
    # Start time logging for test
    start_time = datetime.now()
    print(f"PROCESS STARTED: test_compute_similarity_scores")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {os.getpid()}")

    # Setup test databases
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute(
            "INSERT INTO code_templates (template_code) VALUES ('print(\"hello\")')"
        )
        conn.execute(
            "INSERT INTO code_templates (template_code) VALUES ('def greet(): return \"hello world\"')"
        )

    # Visual processing indicator: progress bar for scoring
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    objective = "hello world"
    scores = compute_similarity_scores(
        objective,
        prod,
        analytics,
        timeout_minutes=1,
    )
    assert scores, "No similarity scores returned"

    # Validate DUAL COPILOT pattern: check analytics for score records
    assert validate_scores(objective, expected_count=len(scores), analytics_db=analytics), "DUAL COPILOT validation failed"

    # Completion summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"TEST COMPLETED: test_compute_similarity_scores in {duration:.2f}s")
