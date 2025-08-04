from pathlib import Path

from enterprise_modules import compliance


def test_score_persistence_and_fetch(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    score = compliance.calculate_compliance_score(0, 3, 0, 0)
    compliance.persist_compliance_score(score, db_path=db)
    assert compliance.get_latest_compliance_score(db_path=db) == score
