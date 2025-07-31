from pathlib import Path
from scripts.validation.complete_root_maintenance_validator import CompleteRootMaintenanceValidator


def create_workspace(tmp_path: Path) -> Path:
    (tmp_path / "logs").mkdir()
    (tmp_path / "reports").mkdir()
    (tmp_path / "results").mkdir()
    (tmp_path / "documentation").mkdir()
    (tmp_path / "config").mkdir()
    return tmp_path


def test_detect_misplaced_files(tmp_path, monkeypatch):
    workspace = create_workspace(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    # misplace files across folders
    (workspace / "error.log").write_text("x")
    (workspace / "reports" / "server.log").write_text("x")
    (workspace / "results" / "analysis.pdf").write_text("x")

    validator = CompleteRootMaintenanceValidator(workspace_path=str(workspace))
    result = validator.validate_complete_compliance()

    paths = {Path(v.file_path).name: v.expected_folder for v in result.violations}

    assert paths.get("error.log") == "logs"
    assert paths.get("server.log") == "logs"
    assert paths.get("analysis.pdf") == "reports"
