from pathlib import Path

import pytest

from enterprise_modules import compliance


def test_score_persistence_and_fetch(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    score = compliance.calculate_compliance_score(0, 3, 0, 0)
    compliance.persist_compliance_score(score, db_path=db)
    assert compliance.get_latest_compliance_score(db_path=db) == score


def test_composite_score_breakdown() -> None:
    score, breakdown = compliance.calculate_composite_score(10, 8, 2, 1, 3)
    assert score == pytest.approx(0.83, rel=1e-3)
    assert breakdown["lint_score"] == pytest.approx(0.9, rel=1e-3)
    assert breakdown["test_score"] == pytest.approx(0.8, rel=1e-3)
    assert breakdown["placeholder_score"] == pytest.approx(0.75, rel=1e-3)
