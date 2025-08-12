"""Tests for QuantumDatabaseSearch."""

import sqlite3
import tempfile
from pathlib import Path

from ghc_quantum.algorithms.database_search import QuantumDatabaseSearch


def create_test_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE items (name TEXT)")
    cur.executemany("INSERT INTO items (name) VALUES (?)", [("alpha",), ("beta",), ("gamma",)])
    conn.commit()
    conn.close()


class TestQuantumDatabaseSearch:
    """Test Grover-based database search."""

    def test_search_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            create_test_db(db_path)
            search = QuantumDatabaseSearch(str(db_path), "items", "name")
            assert search.execute_algorithm("beta") is True

    def test_search_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            create_test_db(db_path)
            search = QuantumDatabaseSearch(str(db_path), "items", "name")
            assert search.execute_algorithm("delta") is False
