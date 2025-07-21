import os

from utils.configuration_utils import load_enterprise_configuration


def test_load_json_config(tmp_path, monkeypatch):
    cfg = tmp_path / "conf.json"
    cfg.write_text('{"a":1}', encoding="utf-8")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    conf = load_enterprise_configuration(str(cfg))
    assert conf["a"] == 1
    assert conf["workspace_root"] == str(tmp_path)


def test_load_yaml_config(tmp_path, monkeypatch):
    cfg = tmp_path / "conf.yaml"
    cfg.write_text('b: 2', encoding="utf-8")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    conf = load_enterprise_configuration(str(cfg))
    assert conf["b"] == 2


def test_env_overrides(tmp_path, monkeypatch):
    cfg = tmp_path / "missing.json"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DATABASE", "db/prod.db")
    monkeypatch.setenv("GH_COPILOT_LOG_LEVEL", "DEBUG")
    conf = load_enterprise_configuration(str(cfg))
    assert conf["database_path"] == "db/prod.db"
    assert conf["logging_level"] == "DEBUG"
