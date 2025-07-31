import scripts.autonomous_setup_and_audit as asa


class DummyValidator:
    def __init__(self):
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


def test_main_calls_validator(monkeypatch, tmp_path):
    dummy = DummyValidator()
    monkeypatch.setattr(asa, "SecondaryCopilotValidator", lambda: dummy)
    monkeypatch.setattr(asa, "init_database", lambda path: None)
    monkeypatch.setattr(asa, "ingest_assets", lambda *a, **k: None)
    monkeypatch.setattr(asa, "run_audit", lambda *a, **k: None)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    asa.main()
    assert dummy.called


def test_main_validator_failure(monkeypatch, tmp_path):
    class FailValidator(DummyValidator):
        def validate_corrections(self, files):
            self.called = True
            return False

    dummy = FailValidator()
    monkeypatch.setattr(asa, "SecondaryCopilotValidator", lambda: dummy)
    monkeypatch.setattr(asa, "init_database", lambda path: None)
    monkeypatch.setattr(asa, "ingest_assets", lambda *a, **k: None)
    monkeypatch.setattr(asa, "run_audit", lambda *a, **k: None)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    asa.main()
    assert dummy.called
