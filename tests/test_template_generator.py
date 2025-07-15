#!/usr/bin/env python3
import sqlite3
from pathlib import Path

from copilot.template_intelligence.generator import TemplateGenerator
import logging


def _create_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE templates ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " template_name TEXT UNIQUE NOT NULL,"
            " template_content TEXT NOT NULL)"
        )
        conn.executemany(
            "INSERT INTO templates (template_name, template_content) VALUES (?, ?)",
            [
                ("greeting", "Hello {name}"),
                ("farewell", "Goodbye {name}"),
            ],
        )


def test_generate_greeting(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "template.db"
    _create_db(db_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    gen = TemplateGenerator(str(workspace))
    result = gen.generate_from_pattern("greeting", {"name": "Alice"})
    assert result == "Hello Alice"


def test_generate_farewell_pattern(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "template.db"
    _create_db(db_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    gen = TemplateGenerator(str(workspace))
    result = gen.generate_from_pattern("fare*", {"name": "Bob"})
    assert result == "Goodbye Bob"
