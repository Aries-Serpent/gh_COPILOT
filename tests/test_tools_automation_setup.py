import sqlite3
from pathlib import Path

from tools import automation_setup


def test_ingest_assets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: tmp_path.parent / "backups",
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")

    called = {"v": False}

    def dummy_validate(self, files):
        called["v"] = True
        return True

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        dummy_validate,
    )

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "prompts"
    templates_dir.mkdir()
    (templates_dir / "temp.md").write_text("template")

    db_dir = tmp_path / "databases"
    db_dir.mkdir()

    monkeypatch.setattr(automation_setup, "DB_PATH", db_dir / "production.db")
    monkeypatch.setattr(automation_setup, "ANALYTICS_DB", db_dir / "analytics.db")
    monkeypatch.setattr(automation_setup, "DOC_DIRS", [docs_dir])
    monkeypatch.setattr(automation_setup, "TEMPLATE_DIRS", [templates_dir])

    automation_setup.init_databases()
    automation_setup.ingest_assets()

    with sqlite3.connect(db_dir / "production.db") as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        template_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0]

    assert doc_count == 1
    assert template_count == 1
    assert pattern_count == 1
    assert called["v"]
