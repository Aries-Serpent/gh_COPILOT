"""Tests for ML pattern recognition with lessons integration."""

from ml_pattern_recognition import PatternRecognizer, SklearnPatternModel, train_pipeline
from utils.lessons_learned_integrator import fetch_lessons_by_tag


def test_pattern_recognizer_stores_lessons(tmp_path):
    training = ["optimize cache", "optimize index"]
    model_path = tmp_path / "model.joblib"
    train_pipeline(training, model_path)
    model = SklearnPatternModel.load(model_path)
    recognizer = PatternRecognizer(model)
    db_path = tmp_path / "lessons.db"
    predictions = recognizer.recognize(["optimize cache"], db_path=db_path)
    assert predictions and predictions[0].startswith("cluster_")
    lessons = fetch_lessons_by_tag("pattern_recognition", db_path=db_path)
    assert lessons

