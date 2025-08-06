"""Tests for compliance scoring helpers."""

from enterprise_modules.compliance import (
    calculate_compliance_score,
    calculate_composite_score,
)


def test_calculate_compliance_score_matches_phase5_tasks() -> None:
    """Compliance score should match the weighted formula in phase5_tasks.md."""

    score = calculate_compliance_score(
        ruff_issues=10,
        tests_passed=80,
        tests_failed=20,
        placeholders_open=5,
        placeholders_resolved=5,
    )
    assert score == 77.0


def test_calculate_composite_score_surfaces_weighted_components() -> None:
    """Composite score should expose individual weighted contributions."""

    score, breakdown = calculate_composite_score(10, 80, 20, 5, 5)

    assert score == 77.0
    assert breakdown["lint_score"] == 90.0
    assert breakdown["test_score"] == 80.0
    assert breakdown["placeholder_score"] == 50.0
    assert breakdown["lint_weighted"] == 27.0
    assert breakdown["test_weighted"] == 40.0
    assert breakdown["placeholder_weighted"] == 10.0
    assert (
        breakdown["lint_weighted"]
        + breakdown["test_weighted"]
        + breakdown["placeholder_weighted"]
        == score
    )


def test_calculate_composite_score_handles_no_tests_or_placeholders() -> None:
    """Score should fall back to lint and placeholder defaults when data missing."""

    score, breakdown = calculate_composite_score(0, 0, 0, 0, 0)

    assert score == 50.0
    assert breakdown["lint_weighted"] == 30.0
    assert breakdown["test_weighted"] == 0.0
    assert breakdown["placeholder_weighted"] == 20.0


def test_calculate_composite_score_perfect_results() -> None:
    """A spotless run should yield a perfect composite score."""

    score, breakdown = calculate_composite_score(0, 10, 0, 0, 0)

    assert score == 100.0
    assert breakdown["lint_weighted"] == 30.0
    assert breakdown["test_weighted"] == 50.0
    assert breakdown["placeholder_weighted"] == 20.0

