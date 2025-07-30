from pathlib import Path
import sqlite3
from scripts.utilities.flake8_corrector_base import (
    WhitespaceCorrector,
    ImportOrderCorrector,
    LineLengthCorrector,
    TrailingWhitespaceCorrector,
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


def test_line_length_corrector(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    long_line = "print('" + "a" * 90 + "')\n"
    f = tmp_path / "bad.py"
    f.write_text(long_line)
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    c = LineLengthCorrector(workspace_path=str(tmp_path))
    c.analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(c.analytics_db) as conn:
        conn.execute("CREATE TABLE correction_logs (event TEXT, path TEXT, module TEXT, level TEXT, timestamp TEXT)")
    assert c.execute_correction()
    assert len(f.read_text().splitlines()) > 1
    with sqlite3.connect(c.analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM correction_logs").fetchone()[0]
    assert count >= 1


def test_trailing_whitespace_corrector(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    f = tmp_path / "bad.py"
    f.write_text("print('hi')    \n")
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    c = TrailingWhitespaceCorrector(workspace_path=str(tmp_path))
    c.analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(c.analytics_db) as conn:
        conn.execute("CREATE TABLE correction_logs (event TEXT, path TEXT, module TEXT, level TEXT, timestamp TEXT)")
    assert c.execute_correction()
    assert f.read_text() == "print('hi')\n"
    with sqlite3.connect(c.analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM correction_logs").fetchone()[0]
    assert count >= 1


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
