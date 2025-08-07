from performance_validation_framework import PerformanceValidationFramework


def test_performance_framework_instantiation() -> None:
    """PerformanceValidationFramework should initialize with the database."""
    framework = PerformanceValidationFramework("databases/production.db")
    assert framework.db_path.name == "production.db"

