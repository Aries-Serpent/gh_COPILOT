import sqlite3
from pathlib import Path

from scripts.database.unified_database_initializer import initialize_database
from scripts.automation import setup_ingest_audit


def test_ingest_assets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "prompts"
    templates_dir.mkdir()
    (templates_dir / "temp.md").write_text("template")

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)

    setup_ingest_audit.ingest_assets(tmp_path)

    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        template_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0]
        ops_count = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]

    assert doc_count >= 1
    assert template_count >= 1
    assert pattern_count >= 1
    # two records from database initialization and one each from docs/templates
    assert ops_count >= 4


def test_main_invokes_validator(monkeypatch, tmp_path: Path) -> None:
    """``main`` should run dual-copilot validation on key databases."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))

    called: dict[str, list[str]] = {}

    class DummyValidator:
        def validate_corrections(self, files: list[str]) -> bool:
            called["files"] = files
            return True

    monkeypatch.setattr(setup_ingest_audit, "SecondaryCopilotValidator", lambda: DummyValidator())
    monkeypatch.setattr(setup_ingest_audit, "chunk_anti_recursion_validation", lambda: None)
    monkeypatch.setattr(setup_ingest_audit, "ensure_databases", lambda *_: None)
    monkeypatch.setattr(setup_ingest_audit, "ingest_assets", lambda *_: None)
    monkeypatch.setattr(setup_ingest_audit, "run_placeholder_audit", lambda *_: None)

    setup_ingest_audit.main()

    expected = [
        str(tmp_path / "databases" / "analytics.db"),
        str(tmp_path / "databases" / "production.db"),
    ]
    assert called.get("files") == expected
