from quantum.hybrid_database_processor import QuantumDatabaseProcessor
from quantum.quantum_integration_orchestrator import QuantumIntegrationOrchestrator


def test_processor_switches_between_modes():
    processor = QuantumDatabaseProcessor(use_quantum=True, hardware_available=False)
    assert processor.process("select * from table")["mode"] == "classical"

    processor = QuantumDatabaseProcessor(use_quantum=True, hardware_available=True)
    assert processor.process("select * from table")["mode"] == "quantum"


def test_orchestrator_database_processing_fallback():
    orchestrator = QuantumIntegrationOrchestrator(use_hardware=False)
    assert orchestrator.process_database("select")["mode"] == "classical"

    orchestrator.executor.use_hardware = True
    assert orchestrator.process_database("select")["mode"] == "quantum"

