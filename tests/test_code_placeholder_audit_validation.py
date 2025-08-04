import secondary_copilot_validator


def test_code_placeholder_audit_triggers_validation(tmp_path, monkeypatch):
    import sys
    import types

    sys.modules.setdefault(
        "scripts.correction_logger_and_rollback",
        types.SimpleNamespace(CorrectionLoggerRollback=object),
    )

    from scripts import code_placeholder_audit

    target_file = tmp_path / "module.py"
    target_file.write_text("print('hi')\n", encoding="utf-8")

    called = {}

    def fake_run(files):
        called["files"] = list(files)
        return True

    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", fake_run)

    class FakeLogger:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def log_change(self, *args, **kwargs):
            pass

        def auto_rollback(self, *args, **kwargs):
            pass

        def summarize_corrections(self):
            pass

    monkeypatch.setattr(code_placeholder_audit, "CorrectionLoggerRollback", FakeLogger)
    monkeypatch.setattr(code_placeholder_audit, "_auto_fill_with_templates", lambda *a, **k: None)
    monkeypatch.setattr(code_placeholder_audit, "remove_unused_placeholders", lambda *a, **k: a[0])
    monkeypatch.setattr(code_placeholder_audit, "validate_enterprise_operation", lambda *a, **k: True)

    results = [{"file": str(target_file), "line": 1, "placeholder": "TODO"}]
    code_placeholder_audit.auto_remove_placeholders(
        results, tmp_path / "prod.db", tmp_path / "analytics.db"
    )

    assert str(target_file) in called.get("files", [])
