"""Unit tests for :mod:`ml_pattern_recognition.recognizer`."""

import time
import pytest

from ml_pattern_recognition.recognizer import (
    PatternRecognizer,
    SklearnPatternModel,
    load_production_data,
)


def test_sklearn_model_fit_predict():
    model = SklearnPatternModel()
    data = ["alpha", "beta"]
    model.fit(data)
    assert model.trained is True
    predictions = model.predict(["alpha"])
    assert predictions and predictions[0].startswith("cluster_")


def test_sklearn_model_predict_requires_training():
    model = SklearnPatternModel()
    with pytest.raises(ValueError):
        model.predict(["alpha"])


def test_pattern_recognizer_learn_and_recognize(tmp_path):
    recognizer = PatternRecognizer()
    recognizer.learn(["cache", "index"])
    db_path = tmp_path / "lessons.db"
    predictions = recognizer.recognize(["cache"], db_path=db_path)
    assert predictions and predictions[0].startswith("cluster_")


def test_pattern_recognizer_invalid_model():
    class BadModel:
        def fit(self, data):  # pragma: no cover - minimal implementation
            pass

    with pytest.raises(TypeError):
        PatternRecognizer(model=BadModel())


def test_load_production_data(tmp_path, monkeypatch):
    monkeypatch.delenv("ML_PATTERN_DATA_PATH", raising=False)
    assert load_production_data() == []
    missing = tmp_path / "missing.txt"
    assert load_production_data(missing) == []
    data_file = tmp_path / "data.txt"
    data_file.write_text("a\n\nb\n", encoding="utf-8")
    assert load_production_data(data_file) == ["a", "b"]
    monkeypatch.setenv("ML_PATTERN_DATA_PATH", str(data_file))
    assert load_production_data() == ["a", "b"]


class DummyModel:
    def __init__(self) -> None:
        self.trained = False

    def fit(self, data):
        self.trained = True

    def predict(self, data):
        if not self.trained:
            raise ValueError("not trained")
        return ["cluster_0" for _ in data]


def test_training_benchmark(benchmark):
    recognizer = PatternRecognizer(model=DummyModel())
    data = ["a", "b"]
    start = time.perf_counter()
    recognizer.learn(data)
    assert time.perf_counter() - start < 1.0
    benchmark(recognizer.learn, data)


def test_inference_benchmark(tmp_path, benchmark):
    recognizer = PatternRecognizer(model=DummyModel())
    data = ["a", "b"]
    recognizer.learn(data)
    start = time.perf_counter()
    recognizer.recognize(["a"], db_path=tmp_path / "bench.db")
    assert time.perf_counter() - start < 1.0
    benchmark(recognizer.recognize, ["a"], db_path=tmp_path / "bench.db")
