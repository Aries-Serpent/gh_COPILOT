import logging
import sqlite3
from archive.consolidated_scripts.documentation_db_analyzer import EnterpriseDatabaseProcessor


def test_process_operations(tmp_path, caplog):
    db_path = tmp_path / "docs.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, title TEXT, content TEXT)"
        )
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?,?)",
            [
                ("1", "README", "Title1", "content1"),
                ("2", "GUIDE", "Title2", "content2"),
            ],
        )

    processor = EnterpriseDatabaseProcessor(database_path=str(db_path))
    with caplog.at_level(logging.INFO):
        assert processor.execute_processing()
    messages = " ".join(caplog.messages)
    assert "Documentation entries: 2" in messages
