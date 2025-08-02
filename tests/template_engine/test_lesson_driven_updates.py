import sqlite3

import template_engine.auto_generator as ag


def test_lessons_from_db_update_templates(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "learning_monitor.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE enhanced_lessons_learned (description TEXT, source TEXT, timestamp TEXT, validation_status TEXT, tags TEXT)"
        )
        conn.execute(
            "INSERT INTO enhanced_lessons_learned VALUES (?,?,?,?,?)",
            ("Prefer dataclasses", "test", "2024", "validated", "style"),
        )
    original_load = ag.load_lessons
    monkeypatch.setattr(ag, "load_lessons", lambda: original_load(db_path=db))
    monkeypatch.setattr(ag, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(ag.TemplateAutoGenerator, "_load_patterns", lambda self: [])
    monkeypatch.setattr(ag.TemplateAutoGenerator, "_load_templates", lambda self: [])
    monkeypatch.setattr(ag, "compute_similarity_scores", lambda *a, **k: [])
    monkeypatch.setattr(ag, "extract_patterns", lambda texts: [])
    monkeypatch.setattr(ag, "quantum_text_score", lambda text: 0.0)
    monkeypatch.setattr(ag, "quantum_similarity_score", lambda a, b: 0.0)
    monkeypatch.setattr(ag, "quantum_cluster_score", lambda m: 0.0)
    gen = ag.TemplateAutoGenerator(analytics_db=tmp_path / "a.db", completion_db=tmp_path / "c.db")
    assert any("Prefer dataclasses" in t for t in gen.templates)
