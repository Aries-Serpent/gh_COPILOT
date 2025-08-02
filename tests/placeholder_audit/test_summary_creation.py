import json
import os

from scripts.code_placeholder_audit import main

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def test_summary_file_created_after_runs(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.py").write_text("# TODO sample\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    dash_compliance = dash_dir / "compliance"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_compliance),
    )

    summary = dash_compliance / "placeholder_summary.json"
    assert summary.exists()
    data1 = json.loads(summary.read_text())
    assert data1.get("findings", 0) >= 1
    assert data1.get("resolved_count") == 0
    denominator1 = data1["findings"] + data1["resolved_count"]
    expected1 = (
        data1["resolved_count"] / denominator1 if denominator1 else 1.0
    )
    assert data1["compliance_score"] == expected1
    assert "progress_status" in data1
    assert "compliance_status" in data1
    assert isinstance(data1.get("placeholder_counts"), dict)

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_compliance),
        update_resolutions=True,
    )

    summary2 = dash_compliance / "placeholder_summary.json"
    assert summary2.exists()
    data2 = json.loads(summary2.read_text())
    assert "findings" in data2
    assert "resolved_count" in data2
    denominator2 = data2["findings"] + data2["resolved_count"]
    expected2 = (
        data2["resolved_count"] / denominator2 if denominator2 else 1.0
    )
    assert data2["compliance_score"] == expected2
    assert "placeholder_counts" in data2


def test_compliance_score_zero_denominator(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "clean.py").write_text("print('clean')\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    dash_compliance = dash_dir / "compliance"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_compliance),
    )

    summary = dash_compliance / "placeholder_summary.json"
    data = json.loads(summary.read_text())
    assert data["findings"] == 0
    assert data["resolved_count"] == 0
    assert data["compliance_score"] == 1.0
