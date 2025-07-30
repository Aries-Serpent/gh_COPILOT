import os
from pathlib import Path
import pytest

from template_engine.pattern_mining_engine import validate_no_recursive_folders


def test_no_false_positive_on_template_dirs(tmp_path: Path) -> None:
    (tmp_path / "template_engine").mkdir()
    (tmp_path / "templates").mkdir()
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    # Should not raise for template_* directories
    validate_no_recursive_folders()


def test_detection_of_forbidden_dirs(tmp_path: Path) -> None:
    (tmp_path / "temp_files").mkdir()
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    with pytest.raises(RuntimeError):
        validate_no_recursive_folders()
