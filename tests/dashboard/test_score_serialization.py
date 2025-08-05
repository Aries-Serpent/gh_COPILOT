import json
import sqlite3

import pytest

import dashboard.enterprise_dashboard as ed


def _prepare_metrics(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text(json.dumps({"metrics": {}}), encoding="utf-8")
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE compliance_scores (timestamp TEXT, score REAL)"
        )
        conn.execute(
            """
            CREATE TABLE code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruff_issues INT,
                tests_passed INT,
                tests_failed INT,
                placeholders_open INT,
                placeholders_resolved INT
            )
            """
        )
        conn.execute(
            "INSERT INTO compliance_scores VALUES ('ts', 84.0)"
        )
        conn.execute(
            """
            INSERT INTO code_quality_metrics (
                ruff_issues, tests_passed, tests_failed,
                placeholders_open, placeholders_resolved
            )
            VALUES (5, 8, 2, 3, 7)
            """
        )
        conn.commit()
    monkeypatch.setattr(ed, "METRICS_FILE", metrics_file)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app.test_client(), ed


def test_metrics_include_composite_score(tmp_path, monkeypatch):
    _, ed_module = _prepare_metrics(tmp_path, monkeypatch)
    data = ed_module._load_metrics()["metrics"]
    assert data["compliance_score"] == 84.0
    assert data["code_quality_score"] == pytest.approx(81.67, rel=1e-3)
    assert data["composite_score"] == pytest.approx(81.67, rel=1e-3)
    assert data["score_breakdown"]["placeholder_score"] == pytest.approx(70.0, rel=1e-3)


def test_dashboard_compliance_route(tmp_path, monkeypatch):
    client, _ = _prepare_metrics(tmp_path, monkeypatch)
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()["metrics"]
    assert data["code_quality_score"] == pytest.approx(81.67, rel=1e-3)
    assert data["score_breakdown"]["lint_score"] == pytest.approx(95.0, rel=1e-3)
