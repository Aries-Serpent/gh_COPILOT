import sqlite3
from pathlib import Path

from template_engine.pattern_mining_engine import extract_patterns, mine_patterns


def test_extract_patterns():
    templates = ["def foo(bar): return bar", "def foo(baz): return baz"]
    patterns = extract_patterns(templates)
    assert any("def foo" in p for p in patterns)


def test_mine_patterns(tmp_path: Path):
    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('def x(): pass')")
    patterns = mine_patterns(prod)
    assert patterns
    with sqlite3.connect(prod) as conn:
        count = conn.execute("SELECT COUNT(*) FROM mined_patterns").fetchone()[0]
    assert count == len(patterns)
