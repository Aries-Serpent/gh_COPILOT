from quantum.ml_pattern_recognition import PatternRecognizer, load_placeholder_data


def test_pattern_recognizer_trains_and_evaluates():
    X, y = load_placeholder_data(n_samples=50, random_state=0)
    recognizer = PatternRecognizer()
    recognizer.train(X, y)
    acc = recognizer.evaluate(X, y)
    assert 0.0 <= acc <= 1.0
