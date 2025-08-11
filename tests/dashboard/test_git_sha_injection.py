import importlib
import sys


def test_git_sha_env_injection(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "testsha")
    sys.modules.pop("dashboard.app", None)
    app_module = importlib.import_module("dashboard.app")
    assert app_module.GIT_SHA == "testsha"
    assert app_module.inject_git_sha()["git_sha"] == "testsha"

