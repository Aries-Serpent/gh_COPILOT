from pathlib import Path
import sqlite3


def test_init_and_audit(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "ext_backups"))
    from scripts.utilities import init_and_audit
    production_db = tmp_path / "databases" / "production.db"
    analytics_db = tmp_path / "databases" / "analytics.db"

    init_and_audit.run()

    assert production_db.exists()
    assert analytics_db.exists()
    with sqlite3.connect(production_db) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='template_placeholders'")
        assert cur.fetchone() is not None
