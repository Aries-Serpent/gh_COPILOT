import os
from pathlib import Path
from unittest.mock import patch

import pytest

with patch.dict(os.environ, {"GH_COPILOT_DISABLE_VALIDATION": "1"}):
    from scripts.continuous_operation_orchestrator import validate_enterprise_operation


def test_validate_enterprise_operation_disallowed_path(tmp_path: Path) -> None:
    disallowed_dir = tmp_path / "temp"
    disallowed_dir.mkdir()
    (disallowed_dir / "dummy.txt").write_text("data")

    with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        with patch("os.getcwd", return_value=str(tmp_path)):
            with pytest.raises(RuntimeError):
                validate_enterprise_operation()

    assert not disallowed_dir.exists()


def test_validate_enterprise_operation_ignores_venv(tmp_path: Path) -> None:
    venv_backup = tmp_path / ".venv" / "lib" / "python" / "site-packages" / "botocore" / "data" / "backup"
    venv_backup.mkdir(parents=True)

    with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": str(tmp_path)}):
        with patch("os.getcwd", return_value=str(tmp_path)):
            assert validate_enterprise_operation()
