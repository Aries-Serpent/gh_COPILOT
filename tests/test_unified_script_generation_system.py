#!/usr/bin/env python3
from pathlib import Path
import shutil

from unittest.mock import patch

from scripts.utilities.unified_script_generation_system import EnterpriseUtility


@patch(
    "scripts.utilities.unified_script_generation_system.UnifiedLegacyCleanupSystem.purge_generated_templates"
)
@patch(
    "scripts.utilities.unified_script_generation_system.SecondaryCopilotValidator.validate_corrections",
    return_value=True,
)
@patch("scripts.utilities.unified_script_generation_system.PatternRecognizer")
def test_template_generation(mock_recognizer, _validate, mock_purge, tmp_path):
    workspace = Path(tmp_path)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    source_db = Path(__file__).resolve().parents[1] / "databases" / "template_documentation.db"
    shutil.copy(source_db, db_dir / "template_documentation.db")

    utility = EnterpriseUtility(str(workspace))
    assert utility.perform_utility_function() is True
    mock_recognizer.return_value.recognize.assert_called()
    mock_purge.assert_called()

    generated_dir = workspace / "generated_templates"
    generated_files = list(generated_dir.glob("template_*.txt"))
    assert generated_files, "Template file was not created"
    content = generated_files[0].read_text()
    assert "# Synthesized template" in content


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
