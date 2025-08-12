from pathlib import Path

import sqlite3
import pytest

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
    assert res["database_solutions"]
    assert res["database_solutions"][0].strip() == 'print("hello world")'
    assert 0.0 < res["confidence_score"] <= 1.0
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
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "greet.tmpl").write_text("print('hi')", encoding="utf-8")
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    code = enhancer.generate_integration_ready_code("greet")
    assert isinstance(code, str)
    with sqlite3.connect(prod) as conn:
        row = conn.execute(
            "SELECT template_name, code FROM generated_solutions WHERE objective=?",
            ("greet",),
        ).fetchone()
    assert row == ("greet", "print('hi')")
    with sqlite3.connect(analytics) as conn:
        duration = conn.execute(
            "SELECT duration FROM generation_log WHERE objective=?", ("greet",)
        ).fetchone()
        steps = [
            r[0]
            for r in conn.execute(
                "SELECT step FROM generation_progress WHERE objective=? ORDER BY step", ("greet",)
            ).fetchall()
        ]
    assert duration is not None
    assert steps == [1, 2, 3]
    assert str(prod) in calls and str(analytics) in calls


def test_anti_recursion_failure(tmp_path: Path) -> None:
    (tmp_path / "forbidden_backup").mkdir()
    with pytest.raises(RuntimeError):
        DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))

