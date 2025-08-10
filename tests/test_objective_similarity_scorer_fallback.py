import importlib
import sys
import types


def test_quantum_text_score_fallback(monkeypatch):
    """Ensure scorer provides a fallback when quantum library is unavailable."""
    monkeypatch.delitem(sys.modules, "template_engine.objective_similarity_scorer", raising=False)
    dummy = types.ModuleType("quantum_algorithm_library_expansion")
    monkeypatch.setitem(sys.modules, "quantum_algorithm_library_expansion", dummy)

    scorer = importlib.import_module("template_engine.objective_similarity_scorer")
    assert scorer.quantum_text_score("demo") == 0.0

    # Remove patched module so subsequent tests import the real implementation.
    monkeypatch.delitem(sys.modules, "template_engine.objective_similarity_scorer", raising=False)
