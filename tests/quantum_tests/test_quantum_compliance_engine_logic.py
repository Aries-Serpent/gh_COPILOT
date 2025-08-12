"""Tests for quantum compliance engine core features."""

from pathlib import Path

import sqlite3
import pytest

from ghc_quantum.quantum_compliance_engine import QuantumComplianceEngine
from ghc_quantum import quantum_compliance_engine as qce_module


@pytest.fixture(autouse=True)
def _no_recursion_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable recursion and environment checks for isolated tests."""
    monkeypatch.setattr(qce_module, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(qce_module, "validate_environment_root", lambda: None)


def test_multi_pattern_match_counts(tmp_path: Path) -> None:
    file = tmp_path / "sample.txt"
    file.write_text("alpha beta alpha gamma")
    engine = QuantumComplianceEngine(tmp_path)
    matches = engine._multi_pattern_match(file, ["alpha", "beta"])
    assert matches["alpha"] == 2
    assert matches["beta"] == 1


def test_quantum_field_redundancy_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = QuantumComplianceEngine()

    # Force backend provider to return None to trigger classical fallback
    monkeypatch.setattr(qce_module, "get_backend", lambda use_hardware: None)

    score = engine._quantum_field_redundancy(0.5)
    assert score == 0.5


def test_cognitive_learning_fetch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE script_templates (template_name TEXT, description TEXT)"
    )
    conn.execute(
        "INSERT INTO script_templates (template_name, description) VALUES (?, ?)",
        ("script_a", "quantum analysis"),
    )
    conn.commit()
    conn.close()

    engine = QuantumComplianceEngine(tmp_path)
    suggestions = engine._cognitive_learning_fetch(["quantum"])
    assert "script_a" in suggestions

