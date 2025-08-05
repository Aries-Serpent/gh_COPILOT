from enterprise_modules.compliance import calculate_code_quality_score


def test_score_returns_ratios_and_score():
    score, breakdown = calculate_code_quality_score(0, 10, 0, 0, 5)
    assert score == 100.0
    assert breakdown["lint_score"] == 100.0
    assert breakdown["test_pass_ratio"] == 1.0
    assert breakdown["placeholder_resolution_ratio"] == 1.0


def test_score_handles_mixed_inputs():
    score, breakdown = calculate_code_quality_score(10, 8, 2, 3, 7)
    assert score == 80.0
    assert breakdown["test_pass_ratio"] == 0.8
    assert breakdown["placeholder_resolution_ratio"] == 0.7


def test_score_handles_zero_tests():
    score, breakdown = calculate_code_quality_score(5, 0, 0, 2, 8)
    assert breakdown["test_pass_ratio"] == 0.0
    assert round(score, 2) == 58.33
