from pathlib import Path
import sqlite3

import pytest

from scripts.compliance_aggregator import aggregate_metrics
from enterprise_modules.compliance import calculate_compliance_score


def test_aggregate_metrics_persist(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    result = aggregate_metrics(
        ruff_issues=5,
        tests_passed=8,
        tests_failed=2,
        placeholders_open=1,
        placeholders_resolved=4,
        sessions_successful=0,
        sessions_failed=0,
        db_path=db,
    )
    expected, breakdown = calculate_compliance_score(5, 8, 2, 1, 4, 0, 0)
    assert result["composite_score"] == expected
    assert result["breakdown"]["placeholder_score"] == breakdown["placeholder_score"]
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT ruff_issues, tests_passed, tests_failed, placeholders_open, placeholders_resolved, composite_score FROM code_quality_metrics"
        ).fetchone()
        assert row == (5, 8, 2, 1, 4, expected)

@pytest.mark.skip("requires full dashboard stack and analytics DB")
def test_composite_score_in_dashboard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "databases" / "analytics.db"
    db.parent.mkdir(parents=True)
    aggregate_metrics(1, 3, 1, 2, placeholders_resolved=1, sessions_successful=0, sessions_failed=0, db_path=db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS todo_fixme_tracking (placeholder_type TEXT, status TEXT)"
        )
        conn.commit()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps import enterprise_dashboard as ed

    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(ed, "COMPLIANCE_DIR", tmp_path / "dashboard" / "compliance")
    from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater

    ed.metrics_updater = ComplianceMetricsUpdater(ed.COMPLIANCE_DIR, test_mode=True)
    ed.metrics_updater._fetch_compliance_metrics = lambda **_: {}
    client = ed.app.test_client()
    data = client.get("/metrics").get_json()
    expected, _ = calculate_compliance_score(1, 3, 1, 2, 1, 0, 0)
    assert data["composite_score"] == expected
