import template_engine.auto_generator as ag
import template_engine.learning_templates as lt


def test_lesson_template_merge(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setattr(ag, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(ag.TemplateAutoGenerator, "_load_patterns", lambda self: ["alpha", "beta"])
    monkeypatch.setattr(ag.TemplateAutoGenerator, "_load_templates", lambda self: [])
    monkeypatch.setattr(ag, "compute_similarity_scores", lambda *a, **k: [])
    monkeypatch.setattr(ag, "extract_patterns", lambda texts: [])
    monkeypatch.setattr(ag, "quantum_text_score", lambda text: 0.0)
    monkeypatch.setattr(ag, "quantum_similarity_score", lambda a, b: 0.0)
    monkeypatch.setattr(ag, "quantum_cluster_score", lambda m: 0.0)
    lesson_func = lambda: {"l": "lesson snippet"}
    monkeypatch.setattr(lt, "get_lesson_templates", lesson_func)
    monkeypatch.setattr(ag, "get_lesson_templates", lesson_func)
    gen = ag.TemplateAutoGenerator(analytics_db=tmp_path / "a.db", completion_db=tmp_path / "c.db")
    assert any("lesson snippet" in t for t in gen.templates)
