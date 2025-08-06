from pathlib import Path
import sqlite3
import tempfile
from db_tools.operations.compliance import DatabaseComplianceChecker
from db_tools.database_synchronization_engine import sync_databases


def test_correct_file_removes_placeholders_and_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "databases").mkdir()
        checker = DatabaseComplianceChecker(workspace_path=str(workspace))
        file_path = workspace / "sample.py"
        file_path.write_text("# TODO: fix me\nprint('hi')  \n", encoding="utf-8")

        result = checker.apply_corrections([str(file_path)])
        assert str(file_path) in result
        content = file_path.read_text(encoding="utf-8")
        assert "TODO" not in content
        assert content.endswith("\n")

        rows = checker.db_connection.execute_query("SELECT success, error_message FROM corrections")
        assert rows and rows[0]["success"] == 1
        assert "removed" in rows[0]["error_message"]


def test_correct_file_failure_logged():
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "databases").mkdir()
        checker = DatabaseComplianceChecker(workspace_path=str(workspace))
        missing_file = workspace / "missing.py"

        result = checker.apply_corrections([str(missing_file)])
        assert str(missing_file) not in result
        rows = checker.db_connection.execute_query("SELECT success, error_message FROM corrections")
        assert rows and rows[0]["success"] == 0
        assert rows[0]["error_message"]


def test_sync_databases_resolves_conflicts(tmp_path):
    src = tmp_path / "src.db"
    tgt = tmp_path / "tgt.db"

    def setup_db(path: Path, rows):
        conn = sqlite3.connect(path)
        conn.execute(
            "CREATE TABLE items (id INTEGER PRIMARY KEY, data TEXT, updated_at TEXT)"
        )
        conn.executemany("INSERT INTO items VALUES (?, ?, ?)", rows)
        conn.commit()
        conn.close()

    setup_db(
        src,
        [
            (1, "alpha", "2024-01-02"),
            (2, "beta", "2024-01-01"),
            (4, "delta", "2024-01-04"),
        ],
    )
    setup_db(
        tgt,
        [
            (1, "old", "2023-12-31"),
            (2, "beta-new", "2024-01-03"),
            (3, "gamma", "2024-01-02"),
        ],
    )

    sync_databases(src, tgt)

    conn = sqlite3.connect(tgt)
    rows = conn.execute(
        "SELECT id, data, updated_at FROM items ORDER BY id"
    ).fetchall()
    conn.close()

    assert rows == [
        (1, "alpha", "2024-01-02"),
        (2, "beta-new", "2024-01-03"),
        (4, "delta", "2024-01-04"),
    ]
