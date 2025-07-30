import sqlite3

from template_engine import template_synchronizer


def test_copy_dry_run(tmp_path, capsys):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("x")
    template_synchronizer.copy_template_file(src, dst, dry_run=True)
    assert not dst.exists()
    assert "dry-run" in capsys.readouterr().out.lower()


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
