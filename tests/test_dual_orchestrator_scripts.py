from scripts.optimization import optimize_to_100_percent, security_compliance_enhancer


def test_optimize_triggers_dual_validation(monkeypatch):
    calls = {"validate": False}

    class DummyValidator:
        def __init__(self, logger=None):
            pass

        def validate_corrections(self, files):
            calls["validate"] = True
            return True

    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.SecondaryCopilotValidator",
        DummyValidator,
    )

    def dummy_opt():
        return {"final_readiness": 100.0}

    monkeypatch.setattr(optimize_to_100_percent, "optimize_to_100_percent", dummy_opt)

    result = optimize_to_100_percent.main()
    assert result is True
    assert calls["validate"]


def test_security_triggers_dual_validation(monkeypatch):
    calls = {"validate": False}

    class DummyValidator:
        def __init__(self, logger=None):
            pass

        def validate_corrections(self, files):
            calls["validate"] = True
            return True

    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.SecondaryCopilotValidator",
        DummyValidator,
    )

    class DummyEnhancer:
        def __init__(self, path):
            pass

        def run_security_enhancement(self):
            return {"enterprise_ready": True}

    monkeypatch.setattr(security_compliance_enhancer, "SecurityComplianceEnhancer", DummyEnhancer)

    result = security_compliance_enhancer.main()
    assert result["enterprise_ready"] is True
    assert calls["validate"]
