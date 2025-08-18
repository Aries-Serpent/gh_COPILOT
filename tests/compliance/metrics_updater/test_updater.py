import pytest

from src.compliance.metrics.updater import MetricsUpdater


def test_default_weighting_and_rounding():
    updater = MetricsUpdater()
    scores = {"lint": 0.75, "tests": 0.5, "placeholders": 1.0}
    # 0.4*0.75 + 0.4*0.5 + 0.2*1.0 = 0.7 -> rounded to 0.7
    assert updater.composite(scores) == 0.7


def test_custom_weights_and_precision():
    updater = MetricsUpdater(weights={"a": 1, "b": 2}, precision=3)
    scores = {"a": 0.3333, "b": 0.6666}
    # Weighted average: (0.3333*1 + 0.6666*2) / 3 = 0.5555 -> rounded to 0.556
    assert updater.composite(scores) == 0.556


def test_zero_total_weight():
    updater = MetricsUpdater(weights={"x": 0, "y": 0})
    assert updater.composite({"x": 1, "y": 1}) == 0.0


def test_scores_clamped_and_negative_weights_ignored():
    """Scores are constrained to ``[0, 1]`` and negative weights skipped."""
    updater = MetricsUpdater(weights={"a": 1, "b": -1, "c": 1})
    scores = {"a": 1.5, "b": 1.0, "c": -0.5}
    # Weight 'b' is negative and ignored.  Scores for 'a' and 'c' are clamped
    # to 1.0 and 0.0 respectively resulting in an average of 0.5.
    assert updater.composite(scores) == 0.5


def test_non_numeric_scores_default_to_zero():
    """NaN, infinite or ``None`` scores contribute ``0`` to the composite."""
    updater = MetricsUpdater()
    scores = {"lint": float("nan"), "tests": float("inf"), "placeholders": None}
    assert updater.composite(scores) == 0.0


def test_negative_precision_raises():
    updater = MetricsUpdater(precision=-1)
    with pytest.raises(ValueError):
        updater.composite({"lint": 1})


def test_missing_scores_default_to_zero():
    """Scores for undefined metrics should be treated as ``0``."""
    updater = MetricsUpdater(weights={"lint": 1, "tests": 1})
    # 'tests' metric is missing and thus contributes 0 to the average
    assert updater.composite({"lint": 0.5}) == 0.25


def test_all_negative_weights_return_zero():
    updater = MetricsUpdater(weights={"a": -1, "b": -2})
    assert updater.composite({"a": 1, "b": 1}) == 0.0


def test_caching_prevents_recomputation(monkeypatch):
    updater = MetricsUpdater()
    calls = []

    def spy(scores):
        calls.append(True)
        return MetricsUpdater._composite_uncached(updater, scores)

    monkeypatch.setattr(updater, "_composite_uncached", spy)
    scores = {"lint": 0.3, "tests": 0.7, "placeholders": 0.5}
    first = updater.composite(scores)
    second = updater.composite(scores)
    assert first == second == pytest.approx(0.5)
    assert len(calls) == 1

