import json
import os
import pytest

try:  # pragma: no cover - optional dependency
    import yaml
except ImportError:  # pragma: no cover
    pytest.skip("PyYAML is required for configuration utils tests", allow_module_level=True)

from utils.configuration_utils import load_enterprise_configuration, operations___init__


def test_load_json_config(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    config_dir = ws / "config"
    config_dir.mkdir(parents=True)
    cfg_file = config_dir / "enterprise.json"
    cfg_file.write_text(json.dumps({"database_path": "db.sqlite"}))
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    cfg = load_enterprise_configuration()
    assert cfg["database_path"] == "db.sqlite"
    assert cfg["workspace_root"] == str(ws)


def test_load_yaml_config(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    config_dir = ws / "config"
    config_dir.mkdir(parents=True)
    cfg_file = config_dir / "enterprise.yaml"
    cfg_file.write_text(yaml.safe_dump({"logging_level": "DEBUG"}))
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    cfg = load_enterprise_configuration(str(cfg_file))
    assert cfg["logging_level"] == "DEBUG"


def test_environment_override(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    config_dir = ws / "config"
    config_dir.mkdir(parents=True)
    cfg_file = config_dir / "enterprise.json"
    cfg_file.write_text("{}")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("DATABASE_PATH", "override.db")
    cfg = load_enterprise_configuration()
    assert cfg["database_path"] == "override.db"


def test_invalid_config(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    config_dir = ws / "config"
    config_dir.mkdir(parents=True)
    cfg_file = config_dir / "enterprise.json"
    cfg_file.write_text("{invalid}")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    try:
        load_enterprise_configuration()
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_operations_init_sets_env(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    config_dir = ws / "config"
    config_dir.mkdir(parents=True)
    cfg_file = config_dir / "enterprise.json"
    cfg_file.write_text("{}")
    cfg = operations___init__(workspace_path=str(ws), config_path=str(cfg_file))
    assert os.environ["GH_COPILOT_WORKSPACE"] == str(ws)
    assert cfg["workspace_root"] == str(ws)
