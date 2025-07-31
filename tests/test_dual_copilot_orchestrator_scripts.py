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
    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        dummy_validate,
    )
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr("sys.argv", [module])
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
    if module.endswith("workspace_optimizer"):
        monkeypatch.setattr(
            "scripts.file_management.workspace_optimizer.WorkspaceOptimizer.optimize",
            lambda self, wp: [],
        )
        monkeypatch.setattr(
            "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
            lambda: Path.cwd(),
        )
        monkeypatch.setattr(
            "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
            lambda: Path.cwd(),
        )
    if module.endswith("quick_filesystem_check"):
        import io

        monkeypatch.setattr("builtins.open", lambda *a, **kw: io.StringIO(""))

    try:
        runpy.run_module(module, run_name="__main__")
    except SystemExit:
        pass
    return called["v"]


def test_optimizer_triggers_dual_validation(monkeypatch):
    assert _runs_with_dual_validation("scripts.optimization.optimize_to_100_percent", monkeypatch)


def test_security_triggers_dual_validation(monkeypatch):
    assert _runs_with_dual_validation("scripts.optimization.security_compliance_enhancer", monkeypatch)


def test_session_manager_triggers_validation(monkeypatch):
    assert _runs_with_dual_validation("scripts.utilities.SESSION_INTEGRITY_MANAGER", monkeypatch)
