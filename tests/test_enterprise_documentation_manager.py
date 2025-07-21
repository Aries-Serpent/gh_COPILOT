import logging
import sqlite3
from deployment.deployment_package_20250710_183234.scripts.enterprise_database_driven_documentation_manager import EnterpriseDatabaseProcessor


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
                ("2", "README", "Title1", "content2"),
            ],
        )

    processor = EnterpriseDatabaseProcessor(database_path=str(db_path))
    with caplog.at_level(logging.INFO):
        assert processor.execute_processing()
    messages = " ".join(caplog.messages)
    assert "Title1: 2 versions" in messages
