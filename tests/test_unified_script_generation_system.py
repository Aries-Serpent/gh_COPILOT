from pathlib import Path
import shutil

from unified_script_generation_system import EnterpriseUtility


def test_template_generation(tmp_path):
    workspace = Path(tmp_path)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    source_db = Path(__file__).resolve().parents[1] / "databases" / "template_documentation.db"
    shutil.copy(source_db, db_dir / "template_documentation.db")

    utility = EnterpriseUtility(str(workspace))
    assert utility.perform_utility_function() is True

    generated_dir = workspace / "generated_templates"
    generated_files = list(generated_dir.glob("template_*.txt"))
    assert generated_files, "Template file was not created"
    content = generated_files[0].read_text()
    assert "# Synthesized template" in content
