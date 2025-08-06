from quantum.ml_pattern_recognition import PatternRecognizer, load_production_data


def test_pattern_recognizer_trains_and_evaluates():
    X, y = load_production_data()
    recognizer = PatternRecognizer()
    recognizer.train(X, y)
    metrics = recognizer.evaluate(X, y, use_quantum=True)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["quantum_score"] <= 1.0
