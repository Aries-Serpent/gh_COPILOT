import sqlite3

from scripts.run_migrations import apply_migrations


def test_apply_migrations_idempotent(tmp_path):
    db_path = tmp_path / "test.db"
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    migration = migrations / "001_create_table.sql"
    migration.write_text("CREATE TABLE sample(id INTEGER PRIMARY KEY);")
    log_path = tmp_path / "migrations.log"

    apply_migrations(db_path, migrations, log_path)

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT name FROM sqlite_master WHERE name='sample'").fetchone()
        count = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == 1

    apply_migrations(db_path, migrations, log_path)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == 1

    log_text = log_path.read_text()
    assert "applied 001_create_table.sql" in log_text
    assert "skipping 001_create_table.sql" in log_text
