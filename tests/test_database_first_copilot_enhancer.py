from pathlib import Path

import sqlite3
import pytest

from template_engine.objective_similarity_scorer import compute_similarity_scores
from scripts.database.database_first_copilot_enhancer import DatabaseFirstCopilotEnhancer


def test_similarity_ranking_and_confidence(tmp_path: Path, monkeypatch) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    prod = db_dir / "production.db"
    analytics = db_dir / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('print(\"hello world\")')")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('print(\"bye world\")')")
        conn.commit()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        "scripts.database.database_first_copilot_enhancer.validate_enterprise_operation",
        lambda *_a, **_k: True,
    )
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    res = enhancer.query_before_filesystem("hello world")
    assert res["database_solutions"][0].strip().startswith("print(\"hello world\")")
    scores = compute_similarity_scores("hello world", production_db=prod, analytics_db=analytics)
    top_score = max(score for _, score in scores)
    assert res["confidence_score"] == pytest.approx(top_score)
    with sqlite3.connect(prod) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM similarity_scores").fetchone()[0]
    assert rows > 0


def test_recursion_guard_failure(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "temp").mkdir()
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    prod = db_dir / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('print(\"hello\")')")
        conn.commit()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        "scripts.database.database_first_copilot_enhancer.validate_enterprise_operation",
        lambda *_a, **_k: True,
    )
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    with pytest.raises(RuntimeError):
        enhancer.query_before_filesystem("hello")


def test_generate_integration_ready_code_logs(monkeypatch, tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    prod = db_dir / "production.db"
    analytics = db_dir / "analytics.db"
    calls: list[str] = []

    def fake_validate(path: str, *_, **__) -> bool:
        calls.append(path)
        return True

    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('print(\"hi\")')")
        conn.commit()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        "scripts.database.database_first_copilot_enhancer.validate_enterprise_operation",
        fake_validate,
    )
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    code = enhancer.generate_integration_ready_code("greet")
    assert isinstance(code, str) and code
    with sqlite3.connect(prod) as conn:
        row = conn.execute(
            "SELECT code FROM generated_solutions WHERE objective=?", ("greet",)
        ).fetchone()
    assert row is not None
    with sqlite3.connect(analytics) as conn:
        row = conn.execute(
            "SELECT duration FROM generation_log WHERE objective=?", ("greet",)
        ).fetchone()
    assert row is not None
    assert str(prod) in calls and str(analytics) in calls

