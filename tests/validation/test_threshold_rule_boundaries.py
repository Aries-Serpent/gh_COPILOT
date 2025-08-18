"""Boundary tests for :class:`ThresholdRule`."""

from validation.core.rules import ThresholdRule


def test_threshold_rule_boundary_pass() -> None:
    rule = ThresholdRule("coverage", 95.0, ">=")
    assert rule.check(95.0)
    assert rule.check({"value": 95.1})


def test_threshold_rule_boundary_fail() -> None:
    rule = ThresholdRule("coverage", 95.0, ">=")
    assert not rule.check(94.99)
