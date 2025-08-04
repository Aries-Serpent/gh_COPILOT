import scripts.orchestrators.unified_wrapup_orchestrator as uwo


def _noop(*args, **kwargs):
    """Helper no-op function for monkeypatching heavy phases."""


def test_execute_unified_wrapup_runs_validators_in_order(monkeypatch):
    calls = []

    def fake_run_dual(primary, secondary):
        primary()
        secondary()
        return True

    monkeypatch.setattr(uwo, "run_dual_copilot_validation", fake_run_dual)

    def primary(self):
        calls.append("primary")
        return True

    def secondary(self):
        calls.append("secondary")
        return True

    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "primary_validate", primary)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "secondary_validate", secondary)

    # Patch heavy phases and storage
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase1_root_discovery", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase2_file_organization", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase3_config_validation", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase4_script_modularization", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase5_compliance_validation", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase6_final_reporting", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_store_wrapup_results", _noop)

    orchestrator = uwo.UnifiedWrapUpOrchestrator()
    result = orchestrator.execute_unified_wrapup()

    assert result.status == "COMPLETED"
    assert calls == ["primary", "secondary", "primary", "secondary"]


def test_execute_unified_wrapup_reports_failure_order(monkeypatch):
    calls = []

    def fake_run_dual(primary, secondary):
        try:
            primary()
        except Exception:
            pass
        secondary()
        raise RuntimeError("validation failed")

    monkeypatch.setattr(uwo, "run_dual_copilot_validation", fake_run_dual)

    def primary(self):
        calls.append("primary")
        raise ValueError("boom")

    def secondary(self):
        calls.append("secondary")
        return True

    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "primary_validate", primary)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "secondary_validate", secondary)

    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase1_root_discovery", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase2_file_organization", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase3_config_validation", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase4_script_modularization", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase5_compliance_validation", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_execute_phase6_final_reporting", _noop)
    monkeypatch.setattr(uwo.UnifiedWrapUpOrchestrator, "_store_wrapup_results", _noop)

    orchestrator = uwo.UnifiedWrapUpOrchestrator()
    result = orchestrator.execute_unified_wrapup()

    assert result.status == "FAILED"
    assert calls == ["primary", "secondary"]
