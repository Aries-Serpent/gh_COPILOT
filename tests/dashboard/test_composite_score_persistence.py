import json
import sqlite3
import pytest

import dashboard.enterprise_dashboard as ed
import dashboard.integrated_dashboard as gui
from enterprise_modules.compliance import (
    calculate_composite_score,
    persist_compliance_score,
    record_code_quality_metrics,
)


def test_composite_score_persisted_and_served(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text(json.dumps({"metrics": {}}), encoding="utf-8")
    db = tmp_path / "analytics.db"
    monkeypatch.setattr(gui, "METRICS_FILE", metrics_file)
    monkeypatch.setattr(gui, "ANALYTICS_DB", db)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)

    score, breakdown = calculate_composite_score(5, 8, 2, 1, 4)
    persist_compliance_score(score, breakdown, db_path=db)
    # ensure persist_compliance_score wrote placeholder_score to history
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT placeholder_score, composite_score FROM compliance_metrics_history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        assert row == (pytest.approx(breakdown["placeholder_score"], rel=1e-3), pytest.approx(score, rel=1e-3))

    record_code_quality_metrics(5, 8, 2, 1, 4, db_path=db)

    client = ed.app.test_client()
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()["metrics"]

    assert data["compliance_score"] == pytest.approx(score, rel=1e-3)
    assert data["composite_score"] == pytest.approx(score, rel=1e-3)
    assert data["score_breakdown"]["placeholder_score"] == pytest.approx(
        breakdown["placeholder_score"], rel=1e-3
    )

