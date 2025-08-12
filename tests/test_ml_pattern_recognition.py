"""Tests for ML pattern recognition with lessons integration."""

from ml_pattern_recognition import PatternRecognizer
from utils.lessons_learned_integrator import fetch_lessons_by_tag
from ghc_quantum.ml_pattern_recognition import (
    PatternRecognizer as QuantumPatternRecognizer,
    load_production_data,
)


def test_pattern_recognizer_stores_lessons(tmp_path):
    training = ["optimize cache", "optimize index"]
    recognizer = PatternRecognizer()
    recognizer.learn(training)
    db_path = tmp_path / "lessons.db"
    predictions = recognizer.recognize(["optimize cache"], db_path=db_path)
    assert predictions and predictions[0].startswith("cluster_")
    lessons = fetch_lessons_by_tag("pattern_recognition", db_path=db_path)
    assert lessons


def test_quantum_recognizer_uses_production_data_and_quantum_score():
    X, y = load_production_data()
    recognizer = QuantumPatternRecognizer()
    recognizer.train(X, y)
    metrics = recognizer.evaluate(X, y, use_quantum=True)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["quantum_score"] <= 1.0

