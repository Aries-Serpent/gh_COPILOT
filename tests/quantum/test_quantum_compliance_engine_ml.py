from quantum.quantum_compliance_engine import QuantumComplianceEngine


def test_ml_pattern_recognition(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quantum.quantum_compliance_engine.validate_no_recursive_folders", lambda: None
    )
    target = tmp_path / "sample.txt"
    target.write_text("quantum compliance pattern pattern analysis quantum compliance")
    engine = QuantumComplianceEngine(tmp_path)
    patterns = engine._ml_pattern_recognition(target, top_n=2)
    assert len(patterns) == 2


def test_score_uses_ml_when_no_patterns(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quantum.quantum_compliance_engine.validate_no_recursive_folders", lambda: None
    )
    target = tmp_path / "sample.txt"
    target.write_text("quantum compliance pattern pattern analysis quantum")
    engine = QuantumComplianceEngine(tmp_path)
    monkeypatch.setattr(engine, "_quantum_field_redundancy", lambda s: s)
    score = engine.score(target, [])
    assert score >= 0.0

