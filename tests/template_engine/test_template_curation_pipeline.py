import sqlite3

from template_engine.template_curation_pipeline import curate_templates


def test_curate_templates_pipeline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    doc_dir = tmp_path / "docs"
    tmpl_dir = tmp_path / "templates"
    doc_dir.mkdir()
    tmpl_dir.mkdir()
    (tmp_path / "artifacts" / "logs" / "template_rendering").mkdir(parents=True)

    (doc_dir / "d1.txt").write_text("documentation")
    (tmpl_dir / "t1.txt").write_text("alpha beta gamma delta epsilon")
    (tmpl_dir / "t2.txt").write_text("alpha beta gamma delta zeta")
    (tmpl_dir / "t3.txt").write_text("alpha beta gamma delta eta")

    production_db = tmp_path / "production.db"
    analytics_db = tmp_path / "analytics.db"

    summary = curate_templates(
        doc_dir,
        tmpl_dir,
        "alpha beta objective",
        production_db=production_db,
        analytics_db=analytics_db,
    )

    assert summary["patterns"]
    assert summary["clusters"] >= 1
    assert len(summary["scores"]) == 3

    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute("SELECT COUNT(*) FROM pattern_cluster_metrics").fetchone()
    assert row[0] == 1

