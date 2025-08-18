from pathlib import Path

from security.validator import validate_security_configs, write_reports


def test_validator_pass(tmp_path: Path) -> None:
    """Validator passes when critical keys are present."""

    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "access_control_matrix.json").write_text(
        '{"directory_permissions": {}}'
    )

    results = validate_security_configs(config_dir)
    assert results["access_control_matrix.json"]["status"] == "pass"

    report_dir = tmp_path / "reports"
    write_reports(results, report_dir)
    assert (report_dir / "security_validator.json").exists()
    assert (report_dir / "security_validator.csv").exists()


def test_validator_fail(tmp_path: Path) -> None:
    """Validator fails when critical keys are missing."""

    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "access_control_matrix.json").write_text("{}")

    results = validate_security_configs(config_dir)
    assert results["access_control_matrix.json"]["status"] == "fail"
