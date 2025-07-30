import runpy
from pathlib import Path


def test_entrypoint_initializes_db(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    called = {}

    def fake_init(path):
        called["path"] = Path(path)
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()

    monkeypatch.setattr(
        "scripts.database.unified_database_initializer.initialize_database",
        fake_init,
    )
    monkeypatch.setattr("dashboard.enterprise_dashboard.main", lambda: None)

    runpy.run_module("scripts.docker_entrypoint", run_name="__main__")

    expected = tmp_path / "databases" / "enterprise_assets.db"
    assert called.get("path") == expected
    assert expected.exists()


def test_entrypoint_skips_existing_db(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    db_path = tmp_path / "databases" / "enterprise_assets.db"
    db_path.parent.mkdir(parents=True)
    db_path.touch()

    called = False

    def fake_init(path):
        nonlocal called
        called = True

    monkeypatch.setattr(
        "scripts.database.unified_database_initializer.initialize_database",
        fake_init,
    )
    monkeypatch.setattr("dashboard.enterprise_dashboard.main", lambda: None)

    runpy.run_module("scripts.docker_entrypoint", run_name="__main__")

    assert not called
