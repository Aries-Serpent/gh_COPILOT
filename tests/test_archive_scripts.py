import importlib
import sqlite3
from pathlib import Path

import pytest

SCRIPTS = [
    "comprehensive_production_deployer",
    "refined_production_builder",
]


@pytest.mark.parametrize("module_name", SCRIPTS)
def test_perform_utility_function(tmp_path, module_name):
    module = importlib.import_module(f"scripts.{module_name}")
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE script_repository (script_path TEXT)")
        conn.execute("INSERT INTO script_repository VALUES ('demo.txt')")
    (tmp_path / "demo.txt").write_text("ok")
    util = module.EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function()


def test_no_placeholders():
    for name in SCRIPTS:
        path = Path("scripts") / f"{name}.py"
        assert "# Implementation placeholder" not in path.read_text()
