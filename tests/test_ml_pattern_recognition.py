from ml_pattern_recognition import PatternRecognizer


def test_stub_recognizer_returns_input():
    recognizer = PatternRecognizer()
    data = ["a", "b"]
    assert recognizer.recognize(data) == data
