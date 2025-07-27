#!/usr/bin/env python3
import sqlite3
from pathlib import Path

import pytest

from scripts.database.database_first_copilot_enhancer import DatabaseFirstCopilotEnhancer


def test_environment_validation(tmp_path: Path) -> None:
    """Workspace with backup folder should raise error."""
    (tmp_path / "my_backup").mkdir()
    with pytest.raises(RuntimeError):
        DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))


def test_query_before_filesystem_order(monkeypatch, tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))

    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE solutions (objective TEXT, code TEXT)")
        conn.execute(
            "INSERT INTO solutions (objective, code) VALUES (?, ?)",
            ("hello", "print('hi')"),
        )
        conn.commit()

    calls = []

    original_db = DatabaseFirstCopilotEnhancer._query_database_solutions

    def spy_db(self, obj):
        calls.append("db")
        return original_db(self, obj)

    original_fs = DatabaseFirstCopilotEnhancer._find_template_matches

    def spy_fs(self, obj):
        calls.append("fs")
        return original_fs(self, obj)

    monkeypatch.setattr(DatabaseFirstCopilotEnhancer, "_query_database_solutions", spy_db)
    monkeypatch.setattr(DatabaseFirstCopilotEnhancer, "_find_template_matches", spy_fs)

    result = enhancer.query_before_filesystem("hello")
    assert result["database_solutions"] == ["print('hi')"]
    assert calls == ["db", "fs"]


def test_similarity_scoring(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))

    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE solutions (objective TEXT, code TEXT)")
        conn.execute(
            "INSERT INTO solutions (objective, code) VALUES (?, ?)",
            ("hello world", "print('hello world')"),
        )
        conn.commit()

    result = enhancer.query_before_filesystem("hello")
    assert "print('hello world')" in result["database_solutions"]


def test_environment_adaptation(tmp_path: Path) -> None:
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    result = enhancer.query_before_filesystem("hello")
    assert str(tmp_path) in result["template_code"]


def test_template_engine_db_and_fs(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
        conn.execute(
            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
            ("greet", "print('hello from db')"),
        )
        conn.commit()
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "fallback.tmpl").write_text("print('fallback')")

    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    assert "hello from db" in enhancer.template_engine("greet")
    assert "fallback" in enhancer.template_engine("missing")


def test_pattern_template_engine(tmp_path: Path) -> None:
    enhancer = DatabaseFirstCopilotEnhancer(workspace_path=str(tmp_path))
    tpl = enhancer.template_engine("database_first_pattern")
    assert "DatabaseFirstOperator" in tpl
