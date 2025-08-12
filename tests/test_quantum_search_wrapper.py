import sqlite3
import sys
from pathlib import Path

from ghc_quantum.quantum_database_search import (
    quantum_search_hybrid,
    quantum_search_nosql,
    quantum_search_sql,
)


def setup_db(path: Path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE items(name TEXT)")
        conn.executemany("INSERT INTO items VALUES (?)", [("a",), ("b",)])


def test_sql_search(tmp_path: Path):
    db = tmp_path / "db.sqlite"
    setup_db(db)
    res = quantum_search_sql("SELECT name FROM items", db)
    assert len(res) == 2


def test_nosql_search(tmp_path: Path):
    db = tmp_path / "db.sqlite"
    setup_db(db)
    res = quantum_search_nosql("items", {"name": "a"}, db)
    assert res[0]["name"] == "a"


def test_hybrid_sql_search(tmp_path: Path):
    db = tmp_path / "db.sqlite"
    setup_db(db)
    res = quantum_search_hybrid("sql", "SELECT name FROM items", db)
    assert {"name": "a"} in res and {"name": "b"} in res


def test_cli_hybrid_modes(monkeypatch, tmp_path: Path, capsys):
    db = tmp_path / "db.sqlite"
    setup_db(db)
    # SQL mode (default when no collection provided)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qds",
            "--type",
            "hybrid",
            "--db",
            str(db),
            "--query",
            "SELECT name FROM items",
        ],
    )
    from ghc_quantum.quantum_database_search import main as cli_main

    cli_main()
    sql_out = capsys.readouterr().out
    assert "Search results (2):" in sql_out

    # NoSQL mode (collection provided)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qds",
            "--type",
            "hybrid",
            "--db",
            str(db),
            "--query",
            "{\"name\": \"a\"}",
            "--collection",
            "items",
        ],
    )
    cli_main()
    nosql_out = capsys.readouterr().out
    assert "Search results (1):" in nosql_out
