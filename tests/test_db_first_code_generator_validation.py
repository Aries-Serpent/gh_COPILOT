import secondary_copilot_validator

def test_db_first_code_generator_triggers_validation(tmp_path, monkeypatch):
    import sys
    import types

    sys.modules.setdefault(
        "scripts.correction_logger_and_rollback",
        types.SimpleNamespace(CorrectionLoggerRollback=object),
    )

    import importlib
    module = importlib.import_module("template_engine.db_first_code_generator")
    Generator = module.DBFirstCodeGenerator

    gen = Generator(
        production_db=tmp_path / "prod.db",
        documentation_db=tmp_path / "docs.db",
        template_db=tmp_path / "templates.db",
        analytics_db=tmp_path / "analytics.db",
    )

    monkeypatch.setattr(
        Generator,
        "select_best_template",
        lambda self, objective: "print('hi')\n",
        raising=False,
    )
    monkeypatch.setattr(
        Generator,
        "generate",
        lambda self, objective: "print('hi')\n",
        raising=False,
    )
    monkeypatch.setattr(
        "template_engine.db_first_code_generator.validate_no_recursive_folders", lambda: None
    )
    monkeypatch.setattr(
        "template_engine.db_first_code_generator.replace_placeholders",
        lambda template, mapping: template,
    )
    monkeypatch.setattr(
        "template_engine.db_first_code_generator.remove_unused_placeholders",
        lambda stub, **kwargs: stub,
    )

    called = {}

    def fake_run(files):
        called["files"] = list(files)
        return True

    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", fake_run)

    path = gen.generate_integration_ready_code("sample_output")

    assert str(path) in called.get("files", [])
