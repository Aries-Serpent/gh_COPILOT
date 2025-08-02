#!/usr/bin/env python3

from scripts.session.session_management_consolidation_executor import EnterpriseUtility


def test_consolidation_executor_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    util = EnterpriseUtility(str(tmp_path))
    assert util.perform_utility_function() is True
    assert util.execute_utility() is True


def test_consolidation_executor_fails_on_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        lambda: tmp_path,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "empty.txt").write_text("")
    util = EnterpriseUtility(str(tmp_path))
    assert util.perform_utility_function() is False
