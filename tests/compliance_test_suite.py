"""Basic smoke tests for stub modules."""

from pathlib import Path

from template_engine.db_first_code_generator import DBFirstCodeGenerator
from template_engine.pattern_clustering_sync import PatternClusteringSync
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater
from quantum.quantum_compliance_engine import QuantumComplianceEngine


def test_db_first_code_generator(tmp_path: Path) -> None:
    gen = DBFirstCodeGenerator(tmp_path / "prod.db", tmp_path / "analytics.db")
    assert gen.generate("test") == ""


def test_pattern_clustering_sync(tmp_path: Path) -> None:
    sync = PatternClusteringSync(tmp_path / "prod.db")
    sync.synchronize_templates()


def test_correction_logger_and_rollback(tmp_path: Path) -> None:
    log = CorrectionLoggerRollback(tmp_path / "analytics.db")
    log.log_change(tmp_path / "file.txt", "test")
    log.rollback(tmp_path / "file.txt")


def test_compliance_metrics_updater(tmp_path: Path) -> None:
    upd = ComplianceMetricsUpdater(tmp_path)
    upd.update()


def test_quantum_compliance_engine(tmp_path: Path) -> None:
    engine = QuantumComplianceEngine()
    assert engine.score(tmp_path) == 0.0
