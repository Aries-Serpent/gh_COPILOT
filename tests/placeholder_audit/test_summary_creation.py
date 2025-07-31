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

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
    )

    summary = dash_dir / "compliance" / "placeholder_summary.json"
    assert summary.exists()
    data1 = json.loads(summary.read_text())
    assert data1.get("findings", 0) >= 1

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
        update_resolutions=True,
    )

    summary2 = dash_dir / "compliance" / "placeholder_summary.json"
    assert summary2.exists()
    data2 = json.loads(summary2.read_text())
    assert "findings" in data2
