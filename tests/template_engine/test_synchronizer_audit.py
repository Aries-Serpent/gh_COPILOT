import sqlite3
from pathlib import Path

import pytest

from template_engine import template_synchronizer as ts


class FailingConn(sqlite3.Connection):
    def execute(self, sql, *args, **kwargs):
        if sql.startswith("INSERT"):
            super().execute(sql, *args, **kwargs)
            raise sqlite3.OperationalError("boom")
        return super().execute(sql, *args, **kwargs)

    def executescript(self, sql):
        raise sqlite3.OperationalError("boom")


def test_copy_template_file_logs_and_rollback(tmp_path, monkeypatch):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    analytics = tmp_path / "analytics.db"
    monkeypatch.setattr(ts, "ANALYTICS_DB", analytics)
    audits = []
    rollbacks = []
    monkeypatch.setattr(ts, "_log_audit_real", lambda db, d: audits.append(d))
    monkeypatch.setattr(ts, "_log_rollback", lambda target, backup=None: rollbacks.append(target))

    ts.copy_template_file(src, dst)

    assert dst.read_text() == "data"
    assert any("src.txt" in a for a in audits)
    assert not rollbacks

    monkeypatch.setattr(Path, "write_text", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        ts.copy_template_file(src, dst)
    assert not dst.exists()
    assert any("failed" in a for a in audits)
    assert rollbacks


def test_update_template_content_failure_logs(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
        conn.execute("INSERT INTO templates VALUES ('old', 'x')")
    file_path = tmp_path / "t.txt"
    file_path.write_text("new")

    audits = []
    rollbacks = []
    monkeypatch.setattr(ts, "_log_audit_real", lambda dbn, det: audits.append(det))
    monkeypatch.setattr(ts, "_log_rollback", lambda target, backup=None: rollbacks.append(target))

    orig_connect = sqlite3.connect
    def connect_patched(*args, **kwargs):
        if args[0] == db:
            kwargs["factory"] = FailingConn
        return orig_connect(*args, **kwargs)
    monkeypatch.setattr(sqlite3, "connect", connect_patched)

    ts.update_template_content([db], "name", file_path)

    with sqlite3.connect(db) as conn:
        rows = list(conn.execute("SELECT name FROM templates ORDER BY name"))
    assert rows == [("old",)]
    assert any("update_failed" in a for a in audits)
    assert rollbacks


def test_run_migrations_failure_logs(tmp_path, monkeypatch):
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

    audits = []
    rollbacks = []
    monkeypatch.setattr(ts, "_log_audit_real", lambda dbn, det: audits.append(det))
    monkeypatch.setattr(ts, "_log_rollback", lambda target, backup=None: rollbacks.append(target))

    orig_connect = sqlite3.connect
    def connect_patched(*args, **kwargs):
        if args[0] == db:
            kwargs["factory"] = FailingConn
        return orig_connect(*args, **kwargs)
    monkeypatch.setattr(sqlite3, "connect", connect_patched)

    ts.run_migrations(db)

    with sqlite3.connect(db) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "foo" not in tables
    assert any("migration_failed" in a for a in audits)
    assert rollbacks
