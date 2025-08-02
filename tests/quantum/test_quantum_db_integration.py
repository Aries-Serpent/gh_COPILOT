import os
import sqlite3
from pathlib import Path

from quantum.quantum_database_search import quantum_search_registered_db
from scripts.database.unified_database_management_system import UnifiedDatabaseManager


def test_quantum_search_registered_db(tmp_path: Path):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "test.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE items(id INTEGER, value TEXT)")
        conn.execute("INSERT INTO items VALUES(1, 'alpha')")
    original = os.environ.pop("GH_COPILOT_WORKSPACE", None)
    mgr = UnifiedDatabaseManager(workspace_root=str(tmp_path))
    try:
        results = quantum_search_registered_db(
            "SELECT value FROM items",
            "test.db",
            use_hardware=False,
            workspace_root=str(tmp_path),
        )
        assert results == [{"value": "alpha"}]
        mgr_results = mgr.quantum_query("test.db", "SELECT value FROM items")
        assert mgr_results == results
    finally:
        if original is not None:
            os.environ["GH_COPILOT_WORKSPACE"] = original
