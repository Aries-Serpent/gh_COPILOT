from pathlib import Path

from scripts.maintenance.file_relocator import _update_imports


def test_update_imports(tmp_path: Path) -> None:
    source = tmp_path / "module_a.py"
    source.write_text("import artifact_manager\nfrom artifact_manager import foo\n")

    _update_imports(tmp_path, "artifact_manager", "scripts.utilities.artifact_manager", git_stage=False)

    updated = source.read_text()
    assert "scripts.utilities.artifact_manager" in updated
    assert "import artifact_manager" not in updated
