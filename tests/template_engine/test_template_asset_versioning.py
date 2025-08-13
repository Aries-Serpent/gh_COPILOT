import sqlite3

from scripts.database.template_asset_ingestor import ingest_templates


def test_template_version_increment(tmp_path, monkeypatch):
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    prompts = workspace / "prompts"
    prompts.mkdir()
    template = prompts / "sample.md"
    template.write_text("v1")

    ingest_templates(workspace)

    db_path = workspace / "databases" / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT version FROM template_assets WHERE template_path=?",
            ("prompts/sample.md",),
        ).fetchall()
        assert rows == [(1,)]

    template.write_text("v2")
    ingest_templates(workspace)

    with sqlite3.connect(db_path) as conn:
        versions = [row[0] for row in conn.execute(
            "SELECT version FROM template_assets WHERE template_path=? ORDER BY version",
            ("prompts/sample.md",),
        ).fetchall()]
        assert versions == [1, 2]
