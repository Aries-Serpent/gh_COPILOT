import json
import sqlite3

import pytest

import dashboard.enterprise_dashboard as ed


def _prepare_metrics(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text(
        json.dumps(
            {
                "metrics": {
                    "compliance_score": 84.0,
                    "code_quality_score": 82.5,
                    "composite_score": 82.5,
                    "score_breakdown": {
                        "placeholder_score": 70.0,
                        "lint_score": 95.0,
                        "test_score": 80.0,
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE compliance_scores (timestamp TEXT, composite_score REAL)"
        )
        conn.commit()
    monkeypatch.setattr(ed, "METRICS_FILE", metrics_file)
    from dashboard import integrated_dashboard as idb
    monkeypatch.setattr(idb, "METRICS_FILE", metrics_file)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app.test_client(), ed


def test_metrics_include_composite_score(tmp_path, monkeypatch):
    _, ed_module = _prepare_metrics(tmp_path, monkeypatch)
    data = ed_module._load_metrics()
    assert data["code_quality_score"] == pytest.approx(82.5, rel=1e-3)
    assert data["composite_score"] == pytest.approx(82.5, rel=1e-3)
    assert data["score_breakdown"]["placeholder_score"] == pytest.approx(70.0, rel=1e-3)


def test_dashboard_compliance_route(tmp_path, monkeypatch):
    client, _ = _prepare_metrics(tmp_path, monkeypatch)
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()["metrics"]
    assert data["code_quality_score"] == pytest.approx(82.5, rel=1e-3)
    assert data["score_breakdown"]["lint_score"] == pytest.approx(95.0, rel=1e-3)
