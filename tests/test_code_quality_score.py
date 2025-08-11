from enterprise_modules.compliance import calculate_compliance_score


def test_score_returns_ratios_and_score():
    score, breakdown = calculate_compliance_score(0, 10, 0, 0, 5, 1, 0)
    assert score == 100.0
    assert breakdown["lint_score"] == 100.0
    assert breakdown["test_pass_ratio"] == 1.0
    assert breakdown["placeholder_resolution_ratio"] == 1.0
    assert breakdown["session_success_ratio"] == 1.0


def test_score_handles_mixed_inputs():
    score, breakdown = calculate_compliance_score(10, 8, 2, 3, 7, 5, 5)
    assert score == 78.0
    assert breakdown["test_pass_ratio"] == 0.8
    assert breakdown["placeholder_resolution_ratio"] == 0.7
    assert breakdown["session_success_ratio"] == 0.5


def test_score_handles_zero_tests():
    score, breakdown = calculate_compliance_score(5, 0, 0, 2, 8, 1, 1)
    assert breakdown["test_pass_ratio"] == 0.0
    assert round(score, 2) == 49.5
