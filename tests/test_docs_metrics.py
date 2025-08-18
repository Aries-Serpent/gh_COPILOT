import sqlite3
import sys
import runpy
from pathlib import Path

import pytest

import types

dummy_tqdm = types.ModuleType("tqdm")

class _DummyTqdm:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, *a, **k):
        pass


dummy_tqdm.tqdm = _DummyTqdm
sys.modules.setdefault("tqdm", dummy_tqdm)

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

    called: dict[str, object] = {}

    def validate(path: Path) -> bool:
        assert path == db_path
        called["primary"] = True
        return True

    class DummyValidator:
        def validate_corrections(self, files, primary_success=None):
            called["secondary"] = (files, primary_success)
            return True

    monkeypatch.setattr(docs_metrics_validator, "validate", validate)
    monkeypatch.setattr(docs_metrics_validator, "SecondaryCopilotValidator", lambda: DummyValidator())

    result = docs_metrics_validator.main(["--db-path", str(db_path)])
    assert result == 0
    assert called["secondary"] == ([], True)


def test_docs_metrics_validator_as_script(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    module = types.ModuleType("validate_docs_metrics")

    def validate(path: Path) -> bool:
        return path == db_path

    module.validate = validate
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

    def validate(path: Path) -> bool:
        return path == db_path

    module.validate = validate
    module.DB_PATH = Path("dummy")
    module.WHITEPAPER_PATH = tmp_path / "whitepaper.md"
    module.WHITEPAPER_PATH.write_text("templates: 0")
    monkeypatch.setitem(sys.modules, "scripts.validate_docs_metrics", module)
    argv = ["docs_metrics_validator.py", "--db-path", str(db_path)]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("scripts.docs_metrics_validator", run_name="__main__")
    assert exc.value.code == 0


def test_generate_and_validate_round_trip(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    db_list = tmp_path / "DATABASE_LIST.md"
    db_list.write_text("- a.db\n")

    readme = tmp_path / "README.md"
    readme.write_text(
        "*Generated on 2000-01-01 00:00:00*\n" "Script Validation: 0 scripts\n" "0 Synchronized Databases\n"
    )
    generated_dir = tmp_path / "documentation" / "generated"
    generated_dir.mkdir(parents=True)
    generated_readme = generated_dir / "README.md"
    generated_readme.write_text(
        "*Generated on 2000-01-01 00:00:00*\n" "Script Validation: 0 scripts\n" "0 Synchronized Databases\n"
    )
    whitepaper = tmp_path / "documentation" / "COMPLETE_TECHNICAL_SPECIFICATIONS_WHITEPAPER.md"
    whitepaper.write_text("3 Templates")

    monkeypatch.setattr(generate_docs_metrics, "DATABASE_LIST", db_list)
    monkeypatch.setattr(generate_docs_metrics, "README_PATHS", [readme, generated_readme])
    monkeypatch.setattr(validate_docs_metrics, "DATABASE_LIST", db_list)
    monkeypatch.setattr(validate_docs_metrics, "README_PATH", readme)
    monkeypatch.setattr(validate_docs_metrics, "GENERATED_README", generated_readme)
    monkeypatch.setattr(validate_docs_metrics, "WHITEPAPER_PATH", whitepaper)
    monkeypatch.setattr(generate_docs_metrics, "_log_event", lambda *a, **k: True)
    generate_docs_metrics.main([
        "--db-path", str(db_path), "--analytics-db", str(tmp_path / "analytics.db")
    ])
    assert validate_docs_metrics.validate(db_path)


def test_generate_metrics_invokes_dual_copilot(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    db_list = tmp_path / "DATABASE_LIST.md"
    db_list.write_text("- a.db\n")
    readme = tmp_path / "README.md"
    readme.write_text(
        "*Generated on 2000-01-01 00:00:00*\n"
        "Script Validation: 0 scripts\n"
        "0 Synchronized Databases\n"
    )

    monkeypatch.setattr(generate_docs_metrics, "DATABASE_LIST", db_list)
    monkeypatch.setattr(generate_docs_metrics, "README_PATHS", [readme])
    monkeypatch.setattr(generate_docs_metrics, "_log_event", lambda *a, **k: True)
    called = {}

    def fake_run(primary, secondary):
        called["primary"] = primary
        called["secondary"] = secondary
        return True

    monkeypatch.setattr(generate_docs_metrics, "run_dual_copilot_validation", fake_run)
    generate_docs_metrics.main([
        "--db-path",
        str(db_path),
        "--analytics-db",
        str(tmp_path / "analytics.db"),
    ])
    assert "primary" in called and "secondary" in called


def test_validator_detects_discrepancies(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path)
    db_list = tmp_path / "DATABASE_LIST.md"
    db_list.write_text("- a.db\n")
    readme = tmp_path / "README.md"
    readme.write_text(
        "*Generated on 2000-01-01 00:00:00*\n"
        "Script Validation: 0 scripts\n"
        "0 Synchronized Databases\n"
    )
    generated_dir = tmp_path / "documentation" / "generated"
    generated_dir.mkdir(parents=True)
    generated_readme = generated_dir / "README.md"
    generated_readme.write_text(
        "*Generated on 2000-01-01 00:00:00*\n"
        "Script Validation: 0 scripts\n"
        "0 Synchronized Databases\n"
    )
    whitepaper = tmp_path / "documentation" / "COMPLETE_TECHNICAL_SPECIFICATIONS_WHITEPAPER.md"
    whitepaper.write_text("0 Templates")

    monkeypatch.setattr(validate_docs_metrics, "DATABASE_LIST", db_list)
    monkeypatch.setattr(validate_docs_metrics, "README_PATH", readme)
    monkeypatch.setattr(validate_docs_metrics, "GENERATED_README", generated_readme)
    monkeypatch.setattr(validate_docs_metrics, "WHITEPAPER_PATH", whitepaper)

    assert not validate_docs_metrics.validate(db_path)

    from scripts import docs_metrics_validator

    class DummyValidator:
        def validate_corrections(self, files, primary_success=None):
            return True

    monkeypatch.setattr(
        docs_metrics_validator, "SecondaryCopilotValidator", lambda: DummyValidator()
    )
    monkeypatch.setattr(docs_metrics_validator, "validate", validate_docs_metrics.validate)
    exit_code = docs_metrics_validator.main(["--db-path", str(db_path)])
    assert exit_code == 1
