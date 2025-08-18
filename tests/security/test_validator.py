import json
import sys

import pytest
import runpy

from security import validator


def test_load_security_configs(tmp_path):
    config = tmp_path / "sample.json"
    config.write_text("{\"a\": 1}")
    configs = validator.load_security_configs(tmp_path)
    assert configs == {"sample.json": {"a": 1}}


def test_validate_security_configs_pass_and_fail(tmp_path):
    good = tmp_path / "encryption_standards.json"
    good.write_text("{\"encryption_requirements\": []}")
    bad = tmp_path / "access_control_matrix.json"
    bad.write_text("{}")
    results = validator.validate_security_configs(tmp_path)
    assert results["encryption_standards.json"] == {"status": "pass", "missing": []}
    assert results["access_control_matrix.json"] == {
        "status": "fail",
        "missing": ["directory_permissions"],
    }


def test_write_reports(tmp_path):
    results = {"file.json": {"status": "pass", "missing": []}}
    validator.write_reports(results, tmp_path)
    assert json.loads((tmp_path / "security_validator.json").read_text()) == results
    csv_lines = (tmp_path / "security_validator.csv").read_text().splitlines()
    assert csv_lines[1] == "file.json,pass,"


def test_main_exit_codes(tmp_path, monkeypatch):
    valid = tmp_path / "security_audit_framework.json"
    valid.write_text("{\"audit_categories\": []}")
    monkeypatch.setattr(
        sys,
        "argv",
        ["validator", "--config-dir", str(tmp_path), "--report-dir", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as exc:
        validator.main()
    assert exc.value.code == 0

    invalid = tmp_path / "enterprise_security_policy.json"
    invalid.write_text("{}")
    monkeypatch.setattr(
        sys,
        "argv",
        ["validator", "--config-dir", str(tmp_path), "--report-dir", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as exc2:
        validator.main()
    assert exc2.value.code == 1


def test_cli_entrypoint(tmp_path, monkeypatch):
    valid = tmp_path / "encryption_standards.json"
    valid.write_text("{\"encryption_requirements\": []}")
    monkeypatch.setattr(
        sys,
        "argv",
        ["validator", "--config-dir", str(tmp_path), "--report-dir", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("security.validator", run_name="__main__")
    assert exc.value.code == 0


def test_load_security_configs_handles_errors(tmp_path):
    invalid = tmp_path / "bad.json"
    invalid.write_text("{")
    unreadable = tmp_path / "unreadable.json"
    unreadable.write_text("{}")
    unreadable.chmod(0)
    configs = validator.load_security_configs(tmp_path)
    assert configs["bad.json"] == {}
    assert configs["unreadable.json"] == {}


def test_main_permission_error(tmp_path, monkeypatch):
    cfg = tmp_path / "security_audit_framework.json"
    cfg.write_text("{\"audit_categories\": []}")

    def fake_write_reports(results, report_dir):
        raise PermissionError

    monkeypatch.setattr(validator, "write_reports", fake_write_reports)
    monkeypatch.setattr(
        sys,
        "argv",
        ["validator", "--config-dir", str(tmp_path), "--report-dir", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as exc:
        validator.main()
    assert exc.value.code == 1
