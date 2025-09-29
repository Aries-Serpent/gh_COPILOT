import pytest


def test_run_cmd_denies_network_tools():
    from gh_copilot.automation.exec import run_cmd

    with pytest.raises(RuntimeError):
        run_cmd(["curl", "--version"], allow_fail=True)
    with pytest.raises(RuntimeError):
        run_cmd(["wget", "--help"], allow_fail=True)
    with pytest.raises(RuntimeError):
        run_cmd(["Invoke-WebRequest", "https://example.com"], allow_fail=True)
    with pytest.raises(RuntimeError):
        run_cmd(["iwr", "https://example.com"], allow_fail=True)

