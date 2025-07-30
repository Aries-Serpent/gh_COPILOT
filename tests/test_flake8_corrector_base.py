from pathlib import Path
from scripts.utilities.flake8_corrector_base import (
    WhitespaceCorrector,
    ImportOrderCorrector,
    LineLengthCorrector,
    IndentationCorrector,
    ComplexityCorrector,
)


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


def test_line_length_corrector(tmp_path: Path) -> None:
    long_line = "print('" + "a" * 90 + "')\n"
    f = tmp_path / "bad.py"
    f.write_text(long_line)
    c = LineLengthCorrector(workspace_path=str(tmp_path))
    assert c.execute_correction()
    assert len(f.read_text().splitlines()) > 1


def test_indentation_corrector(tmp_path: Path) -> None:
    bad_code = "def x():\nprint('hi')\n"
    f = tmp_path / "bad.py"
    f.write_text(bad_code)
    c = IndentationCorrector(workspace_path=str(tmp_path))
    assert c.execute_correction()
    assert f.read_text() == "def x():\n    print('hi')\n"


def test_complexity_corrector(tmp_path: Path) -> None:
    lines = ["    if x == {}:\n        pass\n".format(i) for i in range(11)]
    f = tmp_path / "bad.py"
    f.write_text("def f(x):\n" + "".join(lines))
    c = ComplexityCorrector(workspace_path=str(tmp_path))
    assert c.execute_correction()
    assert f.read_text().startswith("# TODO: reduce complexity")
