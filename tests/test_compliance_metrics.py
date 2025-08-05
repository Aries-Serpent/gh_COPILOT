from utils.validation_utils import calculate_composite_compliance_score


def test_composite_score_returns_components():
    scores = calculate_composite_compliance_score(0, 10, 0, 0)
    assert scores["lint_score"] == 100.0
    assert scores["test_score"] == 100.0
    assert scores["placeholder_score"] == 100.0
    assert scores["composite"] == 100.0


def test_composite_score_mixed_inputs():
    scores = calculate_composite_compliance_score(10, 8, 2, 3)
    assert scores["lint_score"] == 90.0
    assert scores["test_score"] == 80.0
    assert scores["placeholder_score"] == 70.0
    assert scores["composite"] == 82.0


def test_composite_score_handles_zero_tests():
    scores = calculate_composite_compliance_score(5, 0, 0, 2)
    assert scores["lint_score"] == 95.0
    assert scores["test_score"] == 0.0
    assert scores["placeholder_score"] == 80.0
    assert scores["composite"] == 54.0
