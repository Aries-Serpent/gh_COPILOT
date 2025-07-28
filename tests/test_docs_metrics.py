import sqlite3
import sys
import runpy
from pathlib import Path

import pytest

import types

from scripts import generate_docs_metrics, validate_docs_metrics


def _setup_db(path: Path) -> Path:
    db = path / "test.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE enterprise_script_tracking(id INTEGER)")
        conn.execute("CREATE TABLE script_template_patterns(id INTEGER)")
        conn.executemany(
            "INSERT INTO enterprise_script_tracking(id) VALUES (?)",
            [(1,), (2,)],
        )
        conn.executemany(
            "INSERT INTO script_template_patterns(id) VALUES (?)",
            [(1,), (2,), (3,)],
        )
    return db


def test_generate_get_metrics(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    db_list = tmp_path / "DATABASE_LIST.md"
    db_list.write_text("- a.db\n- b.db\n")
    monkeypatch.setattr(generate_docs_metrics, "DATABASE_LIST", db_list)
    metrics = generate_docs_metrics.get_metrics(db_path)
    assert metrics == {"scripts": 2, "templates": 3, "databases": 2}


def test_validate_get_db_metrics(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    db_list = tmp_path / "DATABASE_LIST.md"
    db_list.write_text("- c.db\n")
    monkeypatch.setattr(validate_docs_metrics, "DATABASE_LIST", db_list)
    metrics = validate_docs_metrics.get_db_metrics(db_path)
    assert metrics == {"scripts": 2, "templates": 3, "databases": 1}

def test_docs_metrics_validator_wrapper(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    from scripts import docs_metrics_validator
    monkeypatch.setattr(
        docs_metrics_validator,
        "validate",
        lambda path: path == db_path,
    )

    result = docs_metrics_validator.main(["--db-path", str(db_path)])
    assert result == 0


def test_docs_metrics_validator_as_script(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    module = types.ModuleType("validate_docs_metrics")
    module.validate = lambda path: path == db_path
    module.DB_PATH = Path("dummy")
    monkeypatch.setitem(sys.modules, "validate_docs_metrics", module)
    script = Path(__file__).resolve().parents[1] / "scripts" / "docs_metrics_validator.py"
    argv = [str(script), "--db-path", str(db_path)]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(script), run_name="__main__")
    assert exc.value.code == 0


def test_docs_metrics_validator_module(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    module = types.ModuleType("scripts.validate_docs_metrics")
    module.validate = lambda path: path == db_path
    module.DB_PATH = Path("dummy")
    module.WHITEPAPER_PATH = tmp_path / "whitepaper.md"
    module.WHITEPAPER_PATH.write_text("templates: 0")
    monkeypatch.setitem(sys.modules, "scripts.validate_docs_metrics", module)
    argv = ["docs_metrics_validator.py", "--db-path", str(db_path)]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("scripts.docs_metrics_validator", run_name="__main__")
    assert exc.value.code == 0
