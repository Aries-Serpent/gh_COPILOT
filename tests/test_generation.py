from __future__ import annotations
from pathlib import Path
import sqlite3

from gh_copilot.generation.generate_from_templates import generate


def _seed_docs(db: Path):
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS documentation_templates(
          id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT NOT NULL
        );
        """
    )
    con.execute(
        "INSERT OR REPLACE INTO documentation_templates(id, path, content) VALUES (?,?,?)",
        ("t1", "README", "# Hello {{project}}"),
    )
    con.commit()
    con.close()


def _ensure_analytics(db: Path) -> None:
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS generation_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            source TEXT NOT NULL,
            target_path TEXT NOT NULL,
            template_id TEXT,
            inputs_json TEXT,
            ts TEXT NOT NULL
        );
        """
    )
    con.commit()
    con.close()


def _seed_scripts(db: Path):
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS script_templates(
          id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT NOT NULL
        );
        """
    )
    con.execute(
        "INSERT OR REPLACE INTO script_templates(id, path, content) VALUES (?,?,?)",
        ("s1", "tool", "print('ok')"),
    )
    con.commit()
    con.close()


def test_generate_docs(tmp_path: Path):
    docs_db = tmp_path / "documentation.db"
    analytics_db = tmp_path / "analytics.db"
    _seed_docs(docs_db)
    _ensure_analytics(analytics_db)
    out = tmp_path / "generated"
    files = generate("docs", docs_db, out, analytics_db, params={"project": "X"})
    assert (out / "README.md").exists()
    assert "# Hello X" in (out / "README.md").read_text(encoding="utf-8")


def test_generate_scripts(tmp_path: Path):
    prod_db = tmp_path / "production.db"
    analytics_db = tmp_path / "analytics.db"
    _seed_scripts(prod_db)
    _ensure_analytics(analytics_db)
    out = tmp_path / "generated"
    files = generate("scripts", prod_db, out, analytics_db, params={})
    assert (out / "tool.py").exists()
