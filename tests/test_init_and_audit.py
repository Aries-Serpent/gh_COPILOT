import sqlite3


def test_init_and_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: tmp_path / "ext_backups",
    )
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
