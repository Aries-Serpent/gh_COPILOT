from quantum.quantum_integration_orchestrator import QuantumIntegrationOrchestrator


def test_orchestrator_lists_algorithms() -> None:
    """QuantumIntegrationOrchestrator should return a list of algorithms."""
    orchestrator = QuantumIntegrationOrchestrator()
    assert isinstance(orchestrator.available_algorithms(), list)

