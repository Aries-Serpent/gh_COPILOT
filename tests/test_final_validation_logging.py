import importlib
import sqlite3
from pathlib import Path

import pytest

MODULES = [
    "builds.final.production.builds.artifacts.validation.test_quantum_deploy",
    "builds.final.production.builds.artifacts.validation.quantum_performance_integration_tester",
    "builds.final.production.builds.artifacts.validation.FINAL_COMPREHENSIVE_PRODUCTION_TEST",
    "builds.final.production.builds.artifacts.validation.UNIFIED_DEPLOYMENT_ORCHESTRATOR_TEST_SUITE",
    "builds.final.production.builds.artifacts.validation.comprehensive_production_capability_tester",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_final_validation_logs(tmp_path: Path, module_name: str) -> None:
    module = importlib.import_module(module_name)
    prod_db = tmp_path / "production.db"
    an_db = tmp_path / "analytics.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE t(id INTEGER)")
    util = module.EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function() is True
    with sqlite3.connect(an_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM validation_results").fetchone()[0]
    assert count == 1
