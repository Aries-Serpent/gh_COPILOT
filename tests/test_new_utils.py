import json

import pytest

from utils.general_utils import operations_main
from utils.reporting_utils import (
    generate_json_report,
    generate_markdown_report,
    generate_text_report,
)
from utils.validation_utils import (
    detect_zero_byte_files,
    operations_validate_workspace,
    validate_enterprise_environment,
    validate_path,
)


def test_operations_main(capsys):
    def _main():
        return "ok"

    operations_main(_main)
    assert "ok" in capsys.readouterr().out


def test_generate_json_report(tmp_path):
    out = tmp_path / "report.json"
    generate_json_report({"a": 1}, out)
    assert json.loads(out.read_text()) == {"a": 1}


def test_generate_markdown_report(tmp_path):
    out = tmp_path / "report.md"
    generate_markdown_report({"a": 1}, out, title="T")
    text = out.read_text()
    assert text.startswith("# T") and "**a**" in text


def test_generate_text_report(tmp_path):
    out = tmp_path / "report.txt"
    generate_text_report({"a": 1}, out, title="MyReport")
    text = out.read_text()
    assert text.splitlines()[0] == "MyReport"
    assert "a: 1" in text


def test_detect_zero_byte_files(tmp_path):
    z = tmp_path / "z.txt"
    z.touch()
    (tmp_path / "n.txt").write_text("data")
    files = detect_zero_byte_files(tmp_path)
    assert files == [z]


def test_validate_path(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: ws,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: bk,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    inside = ws / "a.txt"
    inside.touch()
    assert validate_path(inside)
    outside = bk / "b.txt"
    outside.touch()
    assert not validate_path(outside)


def test_operations_validate_workspace(tmp_path, monkeypatch, capsys):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    for name in ["databases", "scripts", "utils", "documentation"]:
        (ws / name).mkdir()
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: ws,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: bk,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    operations_validate_workspace()
    out = json.loads(capsys.readouterr().out)
    assert out["integrity"]["overall_status"] == "VALID"


def test_validate_enterprise_environment_accepts_external_path(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = tmp_path / "backups"
    ws.mkdir()
    bk.mkdir()
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: ws,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: bk,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    assert validate_enterprise_environment()


def test_validate_enterprise_environment_rejects_workspace_path(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = ws / "backups"
    ws.mkdir()
    bk.mkdir()
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: ws,
    )
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_backup_root",
        lambda: bk,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    with pytest.raises(EnvironmentError):
        validate_enterprise_environment()
