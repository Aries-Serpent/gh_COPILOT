import json

from validation import compliance_report_generator as crg
from dashboard import integrated_dashboard as gui


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
