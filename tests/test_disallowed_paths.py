import os
from pathlib import Path
from unittest.mock import patch


with patch.dict(os.environ, {"GH_COPILOT_DISABLE_VALIDATION": "1"}):
    from enterprise_modules.compliance import validate_enterprise_operation


def test_validate_enterprise_operation_disallowed_path(tmp_path: Path) -> None:
    disallowed_dir = tmp_path / "temp"
    disallowed_dir.mkdir()
    (disallowed_dir / "dummy.txt").write_text("data")
    (tmp_path / "logs").mkdir()
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "enterprise.json").write_text('{"forbidden_paths": ["*temp*"]}')

    env = {"GH_COPILOT_WORKSPACE": str(tmp_path), "CONFIG_PATH": str(cfg_dir / "enterprise.json")}
    with patch.dict(os.environ, env):
        with patch("os.getcwd", return_value=str(tmp_path)):
            assert not validate_enterprise_operation()

    assert not disallowed_dir.exists()


def test_validate_enterprise_operation_ignores_venv(tmp_path: Path) -> None:
    venv_backup = tmp_path / ".venv" / "lib" / "python" / "site-packages" / "botocore" / "data" / "backup"
    venv_backup.mkdir(parents=True)
    (tmp_path / "logs").mkdir()

    with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        with patch("os.getcwd", return_value=str(tmp_path)):
            assert validate_enterprise_operation()


def test_validate_enterprise_operation_policy_paths(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "enterprise.json").write_text('{"forbidden_paths": ["*secret*"]}')
    secret = tmp_path / "secret"
    secret.mkdir()
    (tmp_path / "logs").mkdir()

    env = {"GH_COPILOT_WORKSPACE": str(tmp_path), "CONFIG_PATH": str(config_dir / "enterprise.json")}
    with patch.dict(os.environ, env):
        with patch("os.getcwd", return_value=str(tmp_path)):
            assert not validate_enterprise_operation()
    assert not secret.exists()
