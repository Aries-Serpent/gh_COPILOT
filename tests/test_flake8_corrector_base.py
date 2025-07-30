from pathlib import Path
from scripts.utilities.flake8_corrector_base import WhitespaceCorrector, ImportOrderCorrector


def test_whitespace_corrector(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("print('hi')  \n")
    c = WhitespaceCorrector(workspace_path=str(tmp_path))
    assert c.execute_correction()
    assert f.read_text() == "print('hi')\n"


def test_import_order_corrector(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("import os, sys\nprint(sys.path)\n")
    c = ImportOrderCorrector(workspace_path=str(tmp_path))
    assert c.execute_correction()
    text = f.read_text()
    assert "import os" in text and "import sys" in text
