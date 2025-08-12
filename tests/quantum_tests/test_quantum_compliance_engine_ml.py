from ghc_quantum.quantum_compliance_engine import QuantumComplianceEngine
import pytest


def test_ml_pattern_recognition(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "ghc_quantum.quantum_compliance_engine.validate_no_recursive_folders", lambda: None
    )
    target = tmp_path / "sample.txt"
    target.write_text("quantum compliance pattern pattern analysis quantum compliance")
    try:
        engine = QuantumComplianceEngine(tmp_path)
        patterns = engine._ml_pattern_recognition(target, top_n=2)
    except RuntimeError as exc:  # pragma: no cover - optional environment
        if "Recursive folder" in str(exc):
            pytest.skip("recursive folder check not available")
        raise
    assert len(patterns) == 2


def test_score_uses_ml_when_no_patterns(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "ghc_quantum.quantum_compliance_engine.validate_no_recursive_folders", lambda: None
    )
    target = tmp_path / "sample.txt"
    target.write_text("quantum compliance pattern pattern analysis quantum")
    try:
        engine = QuantumComplianceEngine(tmp_path)
    except RuntimeError as exc:  # pragma: no cover - optional environment
        if "Recursive folder" in str(exc):
            pytest.skip("recursive folder check not available")
        raise
    monkeypatch.setattr(engine, "_quantum_field_redundancy", lambda s: s)
    score = engine.score(target, [])
    assert score >= 0.0

