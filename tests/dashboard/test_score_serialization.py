import sqlite3

from pytest import approx

import dashboard.enterprise_dashboard as ed
# ensure CSV export routes are registered
import dashboard.app  # noqa: F401


def _prepare_metrics(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text(
        (
            "{\n"
            "    \"metrics\": {\n"
            "        \"compliance_score\": 84.0,\n"
            "        \"code_quality_score\": 82.5,\n"
            "        \"composite_score\": 82.5,\n"
            "        \"score_breakdown\": {\n"
            "            \"placeholder_score\": 70.0,\n"
            "            \"lint_score\": 95.0,\n"
            "            \"test_score\": 80.0\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        encoding="utf-8",
    )
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "analytics.db"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
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
    assert data["code_quality_score"] == approx(82.5, rel=1e-3)
    assert data["composite_score"] == approx(82.5, rel=1e-3)
    assert data["score_breakdown"]["placeholder_score"] == approx(70.0, rel=1e-3)


def test_dashboard_compliance_route(tmp_path, monkeypatch):
    client, _ = _prepare_metrics(tmp_path, monkeypatch)
    resp = client.get("/dashboard/compliance")
    data = resp.get_json()["metrics"]
    assert data["code_quality_score"] == approx(82.5, rel=1e-3)
    assert data["score_breakdown"]["lint_score"] == approx(95.0, rel=1e-3)


def test_compliance_scores_csv_export(tmp_path, monkeypatch):
    client, ed_module = _prepare_metrics(tmp_path, monkeypatch)
    with sqlite3.connect(ed_module.ANALYTICS_DB) as conn:
        conn.execute(
            "CREATE TABLE compliance_metrics_history (ts TEXT, composite_score REAL, lint_score REAL, test_score REAL, placeholder_score REAL)"
        )
        conn.execute(
            "INSERT INTO compliance_metrics_history VALUES (?,?,?,?,?)",
            ("2024-01-01", 90.0, 80.0, 85.0, 95.0),
        )
        conn.commit()
    resp = client.get("/api/compliance_scores.csv")
    assert resp.status_code == 200
    body = resp.data.decode("utf-8")
    assert "timestamp,composite,lint_score,test_score,placeholder_score" in body
    assert "2024-01-01,90.0,80.0,85.0,95.0" in body
