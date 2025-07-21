from pathlib import Path

from builds.production.builds.artifacts.validation.enterprise_data_migration_synchronization_validator import EnterpriseUtility as MigrationUtility
from builds.production.builds.artifacts.validation.quantum_performance_integration_tester import EnterpriseUtility as PerformanceUtility
from builds.production.builds.artifacts.validation.test_quantum_deploy import EnterpriseUtility as DeployUtility


def test_perform_utility_true(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    (db_dir / "production.db").touch()
    for Util in (MigrationUtility, PerformanceUtility, DeployUtility):
        util = Util(str(tmp_path))
        assert util.perform_utility_function() is True


def test_perform_utility_false(tmp_path: Path) -> None:
    for Util in (MigrationUtility, PerformanceUtility, DeployUtility):
        util = Util(str(tmp_path))
        assert util.perform_utility_function() is False
