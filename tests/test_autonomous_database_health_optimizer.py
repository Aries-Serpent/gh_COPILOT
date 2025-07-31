#!/usr/bin/env python3
"""
Tests for Autonomous Database Health Optimizer
Validates all critical issues mentioned in #212 have been resolved
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import inspect
from scripts.automation.autonomous_database_health_optimizer import AutonomousDatabaseHealthOptimizer


class TestAutonomousDatabaseHealthOptimizer:
    """Test class for Autonomous Database Health Optimizer"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create databases directory
        (workspace / "databases").mkdir(exist_ok=True)
        (workspace / "logs").mkdir(exist_ok=True)

        yield workspace

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def optimizer(self, temp_workspace):
        """Create optimizer instance with temporary workspace"""
        return AutonomousDatabaseHealthOptimizer(workspace_path=str(temp_workspace))

    def test_no_duplicate_method_definitions(self, optimizer):
        """Test that duplicate method definitions have been removed"""
        # Get all methods of the optimizer
        methods = [name for name, method in inspect.getmembers(optimizer, predicate=inspect.ismethod)]

        # Check for learning pattern methods - should only have one consolidated method
        learning_methods = [m for m in methods if "load_learning_patterns" in m]
        assert len(learning_methods) == 1, (
            f"Expected 1 learning pattern method, found {len(learning_methods)}: {learning_methods}"
        )
        assert "_load_learning_patterns" in learning_methods, "Should have consolidated _load_learning_patterns method"

        # Check for optimization history methods - should only have one consolidated method
        history_methods = [m for m in methods if "load_optimization_history" in m]
        assert len(history_methods) == 1, (
            f"Expected 1 optimization history method, found {len(history_methods)}: {history_methods}"
        )
        assert "_load_optimization_history" in history_methods, (
            "Should have consolidated _load_optimization_history method"
        )

    def test_missing_strategy_implementation(self, optimizer):
        """Test that self_healing_integrity_check strategy is implemented"""
        strategies = optimizer._load_enhanced_strategies()

        # Check that self_healing_integrity_check strategy exists
        assert "self_healing_integrity_check" in strategies, "Missing self_healing_integrity_check strategy"

        # Check strategy has required fields
        integrity_strategy = strategies["self_healing_integrity_check"]
        assert "sql_commands" in integrity_strategy, "Strategy missing sql_commands"
        assert "expected_improvement" in integrity_strategy, "Strategy missing expected_improvement"

        # Check strategy has correct SQL commands
        expected_commands = ["PRAGMA integrity_check;", "PRAGMA foreign_key_check;", "PRAGMA quick_check;"]
        assert integrity_strategy["sql_commands"] == expected_commands, (
            f"Unexpected SQL commands: {integrity_strategy['sql_commands']}"
        )

        # Check expected improvement
        assert integrity_strategy["expected_improvement"] == 15.0, (
            f"Unexpected improvement value: {integrity_strategy['expected_improvement']}"
        )

    def test_configuration_initialization_not_duplicated(self, optimizer):
        """Test that configuration is not duplicated"""
        # Check health thresholds
        expected_thresholds = {
            "connection_threshold": 100,
            "query_time_threshold": 5.0,
            "storage_threshold": 0.85,
            "memory_threshold": 0.80,
            "cpu_threshold": 0.75,
        }
        assert optimizer.health_thresholds == expected_thresholds, "Health thresholds not configured correctly"

        # Check optimization strategies
        expected_strategies = {
            "vacuum_analyze": {"priority": 1, "frequency": "daily"},
            "index_optimization": {"priority": 2, "frequency": "weekly"},
            "connection_pooling": {"priority": 3, "frequency": "realtime"},
            "query_optimization": {"priority": 1, "frequency": "continuous"},
        }
        assert optimizer.optimization_strategies == expected_strategies, (
            "Optimization strategies not configured correctly"
        )

    def test_tqdm_import_handling(self):
        """Test that tqdm import is handled gracefully"""
        # Test that tqdm can be imported from the module
        from scripts.automation.autonomous_database_health_optimizer import tqdm

        # Test fallback implementation if real tqdm is not available
        # Create a test instance
        progress_bar = tqdm(total=5, desc="Test Progress")
        assert hasattr(progress_bar, "update"), "tqdm instance should have update method"
        assert hasattr(progress_bar, "set_description"), "tqdm instance should have set_description method"
        assert hasattr(progress_bar, "close"), "tqdm instance should have close method"

        # Test that it doesn't crash
        progress_bar.update(1)
        progress_bar.set_description("Updated")
        progress_bar.close()

    def test_database_health_monitoring(self, optimizer, temp_workspace):
        """Test database health monitoring functionality"""
        # Create a test database
        test_db = temp_workspace / "databases" / "test.db"
        test_db.touch()

        # Monitor database health
        health_metrics = optimizer.monitor_database_health("test.db")

        assert health_metrics is not None, "Health monitoring should return metrics"
        assert health_metrics.database_name == "test.db", "Database name should match"
        assert 0.0 <= health_metrics.health_score <= 1.0, "Health score should be between 0 and 1"
        assert health_metrics.integrity_status in ["GOOD", "ISSUES"], "Integrity status should be valid"
        assert isinstance(health_metrics.issues, list), "Issues should be a list"
        assert isinstance(health_metrics.recommendations, list), "Recommendations should be a list"

    def test_optimization_strategy_execution(self, optimizer, temp_workspace):
        """Test optimization strategy execution"""
        # Create a test database
        test_db = temp_workspace / "databases" / "test.db"
        test_db.touch()

        # Execute optimization strategy
        success = optimizer.execute_optimization_strategy("test.db", "vacuum_analyze")
        assert isinstance(success, bool), "Strategy execution should return boolean"

        # Test with missing strategy
        success = optimizer.execute_optimization_strategy("test.db", "nonexistent_strategy")
        assert success is False, "Non-existent strategy should return False"

    def test_strategy_selection(self, optimizer):
        """Test optimal strategy selection"""
        from scripts.automation.autonomous_database_health_optimizer import DatabaseHealthMetrics
        from datetime import datetime

        # Create test health metrics with integrity issues
        health_metrics = DatabaseHealthMetrics(
            database_name="test.db",
            health_score=0.5,
            connection_count=50,
            query_performance=2.0,
            storage_efficiency=0.9,
            integrity_status="ISSUES",
            last_optimization=datetime.now(),
            issues=["Integrity issues detected"],
            recommendations=["Run integrity check"],
        )

        strategies = optimizer._select_optimal_strategies("test.db", health_metrics)

        # Should include integrity check due to integrity issues
        assert "self_healing_integrity_check" in strategies, "Should include integrity check for integrity issues"

        # Should include other strategies based on health metrics
        assert "vacuum_analyze" in strategies, "Should include vacuum_analyze for low health score"

    def test_learning_patterns_loading(self, optimizer):
        """Test learning patterns loading"""
        # Test that loading doesn't crash
        optimizer._load_learning_patterns()

        # Should initialize learning patterns dict
        assert hasattr(optimizer, "learning_patterns"), "Should have learning_patterns attribute"
        assert isinstance(optimizer.learning_patterns, dict), "Learning patterns should be a dictionary"

    def test_optimization_history_loading(self, optimizer):
        """Test optimization history loading"""
        # Test that loading doesn't crash
        optimizer._load_optimization_history()

        # Should initialize optimization history dict
        assert hasattr(optimizer, "optimization_history"), "Should have optimization_history attribute"
        assert isinstance(optimizer.optimization_history, dict), "Optimization history should be a dictionary"

    def test_autonomous_optimization_cycle(self, optimizer, temp_workspace):
        """Test full autonomous optimization cycle"""
        # Create a few test databases
        for i in range(3):
            test_db = temp_workspace / "databases" / f"test_{i}.db"
            test_db.touch()

        # Mock progress callback
        progress_calls = []

        def mock_progress(total, desc):
            class MockProgress:
                def __init__(self, total, desc):
                    self.total = total
                    self.desc = desc
                    progress_calls.append(f"start_{desc}_{total}")

                def update(self, n):
                    progress_calls.append(f"update_{n}")

                def set_description(self, desc):
                    progress_calls.append(f"desc_{desc}")

                def close(self):
                    progress_calls.append("close")

            return MockProgress(total, desc)

        # Run optimization cycle
        optimizer.run_autonomous_optimization(progress_callback=mock_progress)

        # Check that progress was tracked
        assert len(progress_calls) > 0, "Progress callback should have been called"
        assert any("start_" in call for call in progress_calls), "Should have started progress tracking"
        assert any("close" in call for call in progress_calls), "Should have closed progress tracking"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
