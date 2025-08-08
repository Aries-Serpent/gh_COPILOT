#!/usr/bin/env python3
from pathlib import Path
import shutil

<<<<<<< HEAD
from unittest.mock import patch

from scripts.utilities.unified_script_generation_system import EnterpriseUtility


@patch(
    "scripts.utilities.unified_script_generation_system.pattern_mining_engine.mine_patterns",
    return_value=["alpha"],
)
@patch(
    "scripts.utilities.unified_script_generation_system.QuantumOptimizer.run",
    return_value={"result": {}},
)
@patch(
    "scripts.utilities.unified_script_generation_system.SecondaryCopilotValidator.validate_corrections",
    return_value=True,
)
@patch("scripts.utilities.unified_script_generation_system.PatternRecognizer")
def test_template_generation(mock_recognizer, _validate, mock_run, mock_purge, mock_mine, tmp_path):
=======
from unified_script_generation_system import EnterpriseUtility
import logging


def test_template_generation(tmp_path):
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    workspace = Path(tmp_path)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    source_db = Path(__file__).resolve().parents[1] / "databases" / "template_documentation.db"
    shutil.copy(source_db, db_dir / "template_documentation.db")

    utility = EnterpriseUtility(str(workspace))
    assert utility.perform_utility_function() is True
<<<<<<< HEAD
    mock_recognizer.return_value.recognize.assert_called()
    mock_mine.assert_called()
    mock_run.assert_called()
    mock_purge.assert_called()
=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)

    generated_dir = workspace / "generated_templates"
    generated_files = list(generated_dir.glob("template_*.txt"))
    assert generated_files, "Template file was not created"
    content = generated_files[0].read_text()
    assert "# Synthesized template" in content
<<<<<<< HEAD


@patch(
    "unified_legacy_cleanup_system.UnifiedLegacyCleanupSystem.purge_superseded_scripts"
)
@patch(
    "scripts.utilities.unified_script_generation_system.SecondaryCopilotValidator.validate_corrections",
    return_value=True,
)
@patch("scripts.utilities.unified_script_generation_system.PatternRecognizer")
def test_generation_triggers_cleanup(mock_recognizer, _validate, mock_purge, tmp_path):
    workspace = Path(tmp_path)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    source_db = Path(__file__).resolve().parents[1] / "databases" / "template_documentation.db"
    shutil.copy(source_db, db_dir / "template_documentation.db")

    utility = EnterpriseUtility(str(workspace))
    assert utility.perform_utility_function() is True

    mock_purge.assert_called_once_with(workspace / "generated_templates")
=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
