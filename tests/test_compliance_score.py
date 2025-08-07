from pathlib import Path

import pytest

from enterprise_modules import compliance


def test_score_persistence_and_fetch(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    score = compliance.calculate_compliance_score(1, 2, 0, 0, 0)
    _, breakdown = compliance.calculate_composite_score(1, 2, 0, 0, 0)
    compliance.persist_compliance_score(score, breakdown, db_path=db)
    assert compliance.get_latest_compliance_score(db_path=db) == score


def test_composite_score_breakdown() -> None:
    score, breakdown = compliance.calculate_composite_score(10, 8, 2, 1, 3)
    assert score == pytest.approx(82.0, rel=1e-3)
    assert breakdown["lint_score"] == pytest.approx(90.0, rel=1e-3)
    assert breakdown["test_score"] == pytest.approx(80.0, rel=1e-3)
    assert breakdown["placeholder_score"] == pytest.approx(75.0, rel=1e-3)
