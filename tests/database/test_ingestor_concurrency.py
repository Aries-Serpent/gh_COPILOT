import sqlite3
import threading
from pathlib import Path

from scripts.database.documentation_ingestor import ingest_documentation
from scripts.database.template_asset_ingestor import ingest_templates


def test_ingestors_concurrent_access(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# Doc")

    templates_dir = workspace / "prompts"
    templates_dir.mkdir()
    (templates_dir / "tmpl.md").write_text("# Template")

    (workspace / "databases").mkdir()

    errors: list[Exception] = []

    def run_docs() -> None:
        try:
            ingest_documentation(workspace, docs_dir)
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    def run_templates() -> None:
        try:
            ingest_templates(workspace, templates_dir)
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    t1 = threading.Thread(target=run_docs)
    t2 = threading.Thread(target=run_templates)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert not errors

    db_path = workspace / "databases" / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        template_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]

    assert doc_count == 1
    assert template_count == 1

