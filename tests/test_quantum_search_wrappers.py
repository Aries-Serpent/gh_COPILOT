import sqlite3
from pathlib import Path

from quantum.quantum_database_search import quantum_search_nosql, quantum_search_sql


def test_sql_search(tmp_path: Path):
    db = tmp_path / "q.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE items (name TEXT)")
    conn.executemany("INSERT INTO items VALUES (?)", [("a",), ("b",)])
    conn.commit()
    conn.close()
    res = quantum_search_sql("SELECT name FROM items", db)
    assert len(res) == 2


def test_nosql_search(tmp_path: Path):
    db = tmp_path / "q.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE items (name TEXT)")
    conn.executemany("INSERT INTO items VALUES (?)", [("a",), ("b",)])
    conn.commit()
    conn.close()
    res = quantum_search_nosql("items", {"name": "a"}, db)
    assert res[0]["name"] == "a"
