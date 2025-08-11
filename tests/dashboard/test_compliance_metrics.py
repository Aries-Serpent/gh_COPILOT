import json
import pytest

from validation import compliance_report_generator as crg
from dashboard import integrated_dashboard as gui
import dashboard.enterprise_dashboard as ed
from enterprise_modules.compliance import (
    calculate_compliance_score,
    persist_compliance_score,
)


def test_db_to_ui_propagation(tmp_path, monkeypatch):
    monkeypatch.setattr(crg, "validate_no_recursive_folders", lambda: None)
    ruff = tmp_path / "ruff.txt"
    ruff.write_text("issue1\nissue2\n")
    pytest_file = tmp_path / "pytest.json"
    pytest_file.write_text(json.dumps({"summary": {"total": 2, "passed": 2, "failed": 0}}))
    out_dir = tmp_path / "out"
    db = tmp_path / "analytics.db"
    result = crg.generate_compliance_report(ruff, pytest_file, out_dir, analytics_db=db)

    monkeypatch.setattr(gui, "ANALYTICS_DB", db)
    client = gui.app.test_client()
    response = client.get("/dashboard/compliance")
    html = response.data.decode()
    assert str(result["composite_score"]) in html
    assert result["timestamp"] in html


def test_compliance_metrics_breakdown(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)

    score, breakdown = calculate_compliance_score(1, 4, 1, 0, 0, 0, 0)
    persist_compliance_score(score, breakdown, db)

    client = ed.app.test_client()
    resp = client.get("/compliance-metrics")
    data = resp.get_json()

    assert data["latest"]["composite_score"] == pytest.approx(score, rel=1e-3)
    assert data["latest"]["breakdown"]["lint_score"] == pytest.approx(
        breakdown["lint_score"], rel=1e-3
    )
    assert len(data["trend"]) == 1
