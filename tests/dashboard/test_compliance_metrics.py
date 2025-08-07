import json

from validation import compliance_report_generator as crg
from dashboard import enterprise_dashboard as gui


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
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text(json.dumps({"metrics": {}}))
    monkeypatch.setattr(gui, "METRICS_FILE", metrics_file)
    client = gui.app.test_client()
    response = client.get("/dashboard/compliance/view")
    html = response.data.decode()
    assert "Compliance Metrics" in html
