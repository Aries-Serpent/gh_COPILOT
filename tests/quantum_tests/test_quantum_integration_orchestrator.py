from ghc_quantum.quantum_integration_orchestrator import QuantumIntegrationOrchestrator


def test_orchestrator_simulation_fallback(monkeypatch):
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    orchestrator = QuantumIntegrationOrchestrator(use_hardware=False)
    results = orchestrator.run_plan([{"algorithm": "expansion"}])
    assert results[0]["success"] is True
    assert orchestrator.executor.use_hardware is False
