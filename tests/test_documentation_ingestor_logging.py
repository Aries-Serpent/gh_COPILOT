from pathlib import Path

from scripts.database import documentation_ingestor as di


def test_ingest_documentation_logs_event(tmp_path, monkeypatch):
    workspace = tmp_path
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# test")

    db_dir = workspace / "databases"
    db_dir.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation",
        lambda *a, **k: True,
    )
    monkeypatch.setattr(
        "template_engine.learning_templates.get_dataset_sources", lambda *_a: []
    )
    monkeypatch.setattr(
        "scripts.database.documentation_ingestor.check_database_sizes",
        lambda _p: True,
    )

    logged: dict[str, Path] = {}

    def fake_log(db_path, operation, **_):
        logged["db"] = Path(db_path)
        logged["op"] = operation

    monkeypatch.setattr(di, "log_sync_operation", fake_log)

    di.ingest_documentation(workspace)

    assert logged["op"] == "documentation_ingestion"
    assert logged["db"] == workspace / "databases" / "enterprise_assets.db"
