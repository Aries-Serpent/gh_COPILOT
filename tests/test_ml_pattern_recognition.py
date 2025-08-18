"""Tests for ML pattern recognition with lessons integration."""

import time

import pytest
from pathlib import Path

from ml_pattern_recognition import PatternRecognizer, load_production_data as local_load_data
from utils.lessons_learned_integrator import fetch_lessons_by_tag
from quantum.ml_pattern_recognition import (
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


def test_recognizer_requires_training():
    recognizer = PatternRecognizer()
    with pytest.raises(ValueError):
        recognizer.recognize(["optimize cache"])


def test_learn_empty_dataset_raises():
    recognizer = PatternRecognizer()
    with pytest.raises(ValueError):
        recognizer.learn([])


def test_invalid_model_raises_type_error():
    class BadModel:
        def fit(self, data):  # pragma: no cover - minimal implementation
            pass

    with pytest.raises(TypeError):
        PatternRecognizer(model=BadModel())


def test_load_production_data_branches(tmp_path, monkeypatch):
    monkeypatch.delenv("ML_PATTERN_DATA_PATH", raising=False)
    assert local_load_data() == []
    missing = tmp_path / "missing.txt"
    assert local_load_data(missing) == []
    data_file = tmp_path / "data.txt"
    data_file.write_text("a\n\nb\n", encoding="utf-8")
    assert local_load_data(data_file) == ["a", "b"]
    monkeypatch.setenv("ML_PATTERN_DATA_PATH", str(data_file))
    assert local_load_data() == ["a", "b"]


def test_training_and_inference_speed(tmp_path):
    data = [f"text {i}" for i in range(100)]
    recognizer = PatternRecognizer()
    start = time.perf_counter()
    recognizer.learn(data)
    train = time.perf_counter() - start
    start = time.perf_counter()
    recognizer.recognize(data, db_path=tmp_path / "bench.db")
    infer = time.perf_counter() - start
    assert train < 1.0
    assert infer < 1.0


def test_recognize_uses_default_db(monkeypatch):
    captured = {}

    def fake_store(lessons, db_path=Path("dummy")):
        captured["db_path"] = db_path
        captured["count"] = len(lessons)

    monkeypatch.setattr(
        "ml_pattern_recognition.recognizer.store_lessons", fake_store
    )
    recognizer = PatternRecognizer()
    recognizer.learn(["cache", "index"])
    recognizer.recognize(["cache"])
    assert captured["count"] == 1


def test_quantum_recognizer_uses_production_data_and_quantum_score():
    X, y = load_production_data()
    recognizer = QuantumPatternRecognizer()
    recognizer.train(X, y)
    metrics = recognizer.evaluate(X, y, use_quantum=True)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["quantum_score"] <= 1.0

