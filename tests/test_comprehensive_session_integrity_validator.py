from pathlib import Path

from scripts.validation.comprehensive_session_integrity_validator import run_validation


def test_run_validation_success(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    report, success = run_validation(str(tmp_path))
    assert success
    assert report["status"] == "passed"
    assert Path(report["workspace"]) == tmp_path


def test_run_validation_detects_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    (tmp_path / "bad.txt").touch()
    report, success = run_validation(str(tmp_path))
    assert not success
    assert report["status"] in {"failed", "error"}
