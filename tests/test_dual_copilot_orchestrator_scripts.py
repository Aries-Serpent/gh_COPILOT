import runpy


def _runs_with_dual_validation(module: str, monkeypatch) -> bool:
    called = {"v": False}

    def dummy_validate(self, files):
        called["v"] = True
        return True

    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.SecondaryCopilotValidator.validate_corrections",
        dummy_validate,
    )
    if module.endswith("security_compliance_enhancer"):
        import io
        from pathlib import Path

        monkeypatch.setattr(Path, "mkdir", lambda self, *a, **kw: None)
        monkeypatch.setattr("builtins.open", lambda *a, **kw: io.StringIO(""))
        dummy = type(
            "Dummy",
            (),
            {"run_security_enhancement": lambda self: {"enterprise_ready": True}, "__init__": lambda self, wp: None},
        )
        monkeypatch.setattr(
            "scripts.optimization.security_compliance_enhancer.SecurityComplianceEnhancer",
            dummy,
        )
    if module.endswith("optimize_to_100_percent"):
        monkeypatch.setattr(
            "scripts.optimization.optimize_to_100_percent.optimize_to_100_percent",
            lambda: {"final_readiness": 100.0},
        )
        monkeypatch.setattr(
            "scripts.optimization.optimize_to_100_percent.finalize_100_percent_achievement",
            lambda: True,
        )

    try:
        runpy.run_module(module, run_name="__main__")
    except SystemExit:
        pass
    return called["v"]


def test_optimizer_triggers_dual_validation(monkeypatch):
    assert _runs_with_dual_validation("scripts.optimization.optimize_to_100_percent", monkeypatch)


def test_security_triggers_dual_validation(monkeypatch):
    assert _runs_with_dual_validation("scripts.optimization.security_compliance_enhancer", monkeypatch)
