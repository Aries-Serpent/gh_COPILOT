import subprocess
import types

import pytest

from gh_copilot.automation.exec import run_cmd


def test_run_cmd_sets_no_network_env(monkeypatch, tmp_path):
    captured = {}

    def fake_run(argv, cwd, capture_output, text, timeout, check, env):
        captured["argv"] = argv
        captured["env"] = env
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.delenv("NO_NETWORK_EXEC", raising=False)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_cmd(["python", "--version"])

    assert captured["env"]["NO_NETWORK_EXEC"] == "1"
    assert result["code"] == 0


def test_run_cmd_allow_fail(monkeypatch, tmp_path):
    def fake_run(argv, cwd, capture_output, text, timeout, check, env):
        return types.SimpleNamespace(returncode=2, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_cmd(["python", "-c", "exit(2)"], allow_fail=True)

    assert result["code"] == 2


def test_run_cmd_blocks_network_tools():
    with pytest.raises(RuntimeError):
        run_cmd(["curl", "https://example.com"])
