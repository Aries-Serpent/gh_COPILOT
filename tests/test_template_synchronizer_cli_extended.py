import sqlite3
from pathlib import Path
import pytest

from template_engine import template_synchronizer


def test_copy_dry_run(tmp_path, capsys):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("x")
    template_synchronizer.copy_template_file(src, dst, dry_run=True)
    assert not dst.exists()
    assert "dry-run" in capsys.readouterr().out.lower()


def test_copy_failure_rollback(tmp_path, monkeypatch):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("x")
    analytics = tmp_path / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    logs: list[str] = []
    monkeypatch.setattr(template_synchronizer, "_log_audit_real", lambda dbn, det: logs.append(det))

    orig_write = Path.write_text

    def fail_write(self, *args, **kwargs):
        if self == dst:
            raise RuntimeError("boom")
        return orig_write(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_write)
    with pytest.raises(RuntimeError):
        template_synchronizer.copy_template_file(src, dst)
    assert not dst.exists()
    assert any("failed" in log for log in logs)


def test_update_rollback(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    file_path = tmp_path / "t.txt"
    file_path.write_text("foo")
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE other(id INTEGER)")
    logs: list[str] = []
    monkeypatch.setattr(template_synchronizer, "_log_audit_real", lambda dbn, det: logs.append(det))
    template_synchronizer.update_template_content([db], "name", file_path)
    with sqlite3.connect(db) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert tables == [("other",)]
    assert any("update_failed" in d for d in logs)


def test_update_dry_run(tmp_path, capsys):
    db = tmp_path / "test.db"
    file_path = tmp_path / "t.txt"
    file_path.write_text("foo")
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
    template_synchronizer.update_template_content([db], "name", file_path, dry_run=True)
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT * FROM templates").fetchall()
    assert rows == []
    assert "dry-run" in capsys.readouterr().out.lower()


def test_run_migrations_failure(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE templates(name TEXT)")

    mig_dir = tmp_path / "migrations"
    mig_dir.mkdir()
    script = mig_dir / "001.sql"
    script.write_text("CREATE TABLE foo(id INTEGER);")

    orig_glob = Path.glob

    def glob_patched(self, pattern):
        if self == Path("databases/migrations"):
            return [script]
        return orig_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", glob_patched)

    analytics = tmp_path / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    logs: list[str] = []
    monkeypatch.setattr(template_synchronizer, "_log_audit_real", lambda dbn, det: logs.append(det))

    class FailingConn(sqlite3.Connection):
        def executescript(self, sql):
            raise sqlite3.OperationalError("boom")

    orig_connect = sqlite3.connect

    def connect_patched(*args, **kwargs):
        kwargs["factory"] = FailingConn
        return orig_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_patched)

    template_synchronizer.run_migrations(db)
    with sqlite3.connect(db) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "foo" not in tables
    assert any("migration_failed" in log for log in logs)
