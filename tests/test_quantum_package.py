"""
Tests for the quantum package.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from ghc_quantum.algorithms.base import QuantumAlgorithmBase
from ghc_quantum.algorithms.expansion import QuantumLibraryExpansion
from ghc_quantum.algorithms.functional import QuantumFunctional
from ghc_quantum.algorithms.clustering import QuantumClustering
from ghc_quantum.orchestration.registry import QuantumAlgorithmRegistry, get_global_registry
from ghc_quantum.orchestration.executor import QuantumExecutor
from ghc_quantum.utils.quantum_math import QuantumMath
from ghc_quantum.utils.optimization import PerformanceOptimizer


class MockQuantumAlgorithm(QuantumAlgorithmBase):
    """Mock quantum algorithm for testing"""

    def get_algorithm_name(self) -> str:
        return "Mock Algorithm"

    def execute_algorithm(self) -> bool:
        return True


class TestQuantumAlgorithmBase:
    """Test base quantum algorithm functionality"""

    def test_initialization(self):
        """Test algorithm initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            algorithm = MockQuantumAlgorithm(temp_dir)
            assert algorithm.workspace_path == Path(temp_dir)

    def test_execute_utility(self):
        """Test utility execution"""
        algorithm = MockQuantumAlgorithm()
        result = algorithm.execute_utility()
        assert result is True

        stats = algorithm.get_execution_stats()
        assert stats["algorithm"] == "Mock Algorithm"
        assert stats["success"] is True
        assert "duration_seconds" in stats

    def test_validate_workspace(self):
        """Test workspace validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            algorithm = MockQuantumAlgorithm(temp_dir)
            assert algorithm.validate_workspace() is True

        # Test with non-existent path
        algorithm = MockQuantumAlgorithm("/nonexistent/path")
        assert algorithm.validate_workspace() is False


class TestQuantumLibraryExpansion:
    """Test quantum library expansion algorithm"""

    def test_initialization(self):
        """Test expansion algorithm initialization"""
        expansion = QuantumLibraryExpansion()
        assert expansion.get_algorithm_name() == "Quantum Library Expansion"

    @patch("ghc_quantum.algorithms.expansion.AerSimulator")
    def test_grover_demo(self, mock_simulator):
        """Test Grover demonstration"""
        # Mock the quantum simulator
        mock_backend = MagicMock()
        mock_simulator.return_value = mock_backend

        mock_result = MagicMock()
        mock_result.get_counts.return_value = {"11": 150, "00": 50}
        mock_backend.run.return_value.result.return_value = mock_result

        expansion = QuantumLibraryExpansion()
        result = expansion.perform_grover_demo()
        assert result is True  # '11' is the target state


class TestQuantumFunctional:
    """Test quantum functional algorithms"""

    def test_initialization(self):
        """Test functional algorithm initialization"""
        functional = QuantumFunctional()
        assert functional.get_algorithm_name() == "Quantum Functional Algorithms"

    @patch("ghc_quantum.algorithms.functional.AerSimulator")
    def test_grover_search(self, mock_simulator):
        """Test Grover search algorithm"""
        # Mock the quantum simulator
        mock_backend = MagicMock()
        mock_simulator.return_value = mock_backend

        mock_result = MagicMock()
        mock_result.get_counts.return_value = {"10": 512, "01": 512}  # Index 2 in binary
        mock_backend.run.return_value.result.return_value = mock_result

        functional = QuantumFunctional()
        result = functional.run_grover_search([1, 2, 3, 4], 3)

        assert "index" in result
        assert "time" in result
        assert "iterations" in result

    def test_kmeans_clustering(self):
        """Test KMeans clustering"""
        functional = QuantumFunctional()
        result = functional.run_kmeans_clustering(samples=20, clusters=2)

        assert "inertia" in result
        assert "time" in result
        assert result["inertia"] > 0

    def test_simple_qnn(self):
        """Test simple QNN classifier"""
        functional = QuantumFunctional()
        result = functional.run_simple_qnn()

        assert "accuracy" in result
        assert "time" in result
        assert 0 <= result["accuracy"] <= 1


class TestQuantumClustering:
    """Test quantum clustering algorithm"""

    def test_initialization(self):
        """Test clustering algorithm initialization"""
        clustering = QuantumClustering()
        assert clustering.get_algorithm_name() == "Quantum Clustering File Organization"

    def test_clustering_with_files(self):
        """Test clustering with actual files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            for i in range(5):
                (Path(temp_dir) / f"test_{i}.txt").write_text(f"Content {i}")

            clustering = QuantumClustering(workspace_path=temp_dir, n_clusters=2)
            result = clustering.execute_algorithm()
            assert result is True

            stats = clustering.get_execution_stats()
            assert stats["files_clustered"] == 5
            assert stats["n_clusters"] == 2

    def test_clustering_empty_directory(self):
        """Test clustering with empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            clustering = QuantumClustering(workspace_path=temp_dir)
            result = clustering.execute_algorithm()
            assert result is False

    def test_determine_optimal_clusters(self):
        """Test optimal cluster determination"""
        clustering = QuantumClustering()

        # Test with minimal data
        optimal = clustering.determine_optimal_clusters([[1, 2]])
        assert optimal == 1

        # Test with more data points
        import numpy as np

        features = np.random.rand(10, 2)
        optimal = clustering.determine_optimal_clusters(features)
        assert 1 <= optimal <= 10


class TestQuantumAlgorithmRegistry:
    """Test quantum algorithm registry"""

    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = QuantumAlgorithmRegistry()
        algorithms = registry.list_algorithms()

        # Check that built-in algorithms are registered
        assert "expansion" in algorithms
        assert "functional" in algorithms
        assert "clustering" in algorithms

    def test_register_algorithm(self):
        """Test algorithm registration"""
        registry = QuantumAlgorithmRegistry()
        registry.register_algorithm("mock", MockQuantumAlgorithm)

        assert "mock" in registry.list_algorithms()
        assert registry.get_algorithm("mock") == MockQuantumAlgorithm

    def test_create_algorithm(self):
        """Test algorithm creation"""
        registry = QuantumAlgorithmRegistry()
        algorithm = registry.create_algorithm("expansion")

        assert algorithm is not None
        assert isinstance(algorithm, QuantumLibraryExpansion)

    def test_get_algorithm_info(self):
        """Test algorithm info retrieval"""
        registry = QuantumAlgorithmRegistry()
        info = registry.get_algorithm_info("expansion")

        assert info is not None
        assert info["name"] == "expansion"
        assert "class_name" in info
        assert "algorithm_name" in info

    def test_global_registry(self):
        """Test global registry access"""
        global_registry = get_global_registry()
        assert isinstance(global_registry, QuantumAlgorithmRegistry)
        assert len(global_registry.list_algorithms()) >= 3


class TestQuantumExecutor:
    """Test quantum algorithm executor"""

    def test_executor_initialization(self):
        """Test executor initialization"""
        executor = QuantumExecutor(max_workers=2)
        assert executor.max_workers == 2

    def test_execute_algorithm(self):
        """Test single algorithm execution"""
        executor = QuantumExecutor()
        result = executor.execute_algorithm("expansion")

        assert "algorithm" in result
        assert "success" in result
        assert "execution_time" in result
        assert result["algorithm"] == "expansion"

    def test_execute_nonexistent_algorithm(self):
        """Test execution of non-existent algorithm"""
        executor = QuantumExecutor()
        result = executor.execute_algorithm("nonexistent")

        assert result["success"] is False
        assert "error" in result

    def test_execution_summary(self):
        """Test execution summary"""
        executor = QuantumExecutor()

        # Execute some algorithms
        executor.execute_algorithm("expansion")
        executor.execute_algorithm("functional")

        summary = executor.get_execution_summary()
        assert summary["total_executions"] == 2
        assert summary["successful_executions"] >= 0
        assert len(summary["algorithms_used"]) == 2

    def test_algorithm_performance(self):
        """Test algorithm performance metrics"""
        executor = QuantumExecutor()

        # Execute algorithm multiple times
        executor.execute_algorithm("expansion")
        executor.execute_algorithm("expansion")

        perf = executor.get_algorithm_performance("expansion")
        assert perf["algorithm"] == "expansion"
        assert perf["executions"] == 2
        assert "average_time" in perf
        assert "success_rate" in perf


class TestQuantumMath:
    """Test quantum mathematical utilities"""

    def test_calculate_grover_iterations(self):
        """Test Grover iterations calculation"""
        # Test with different numbers of items
        assert QuantumMath.calculate_grover_iterations(1) == 1
        assert QuantumMath.calculate_grover_iterations(4) >= 1
        assert QuantumMath.calculate_grover_iterations(16) >= 2

    def test_calculate_quantum_advantage(self):
        """Test quantum advantage calculation"""
        advantage = QuantumMath.calculate_quantum_advantage(10.0, 2.0)
        assert advantage == 5.0

        # Test edge case
        advantage = QuantumMath.calculate_quantum_advantage(10.0, 0.0)
        assert advantage == float("inf")

    def test_estimate_quantum_fidelity(self):
        """Test quantum fidelity estimation"""
        counts = {"00": 800, "01": 100, "10": 50, "11": 50}
        fidelity = QuantumMath.estimate_quantum_fidelity(counts, "00")
        assert fidelity == 0.8

        # Test edge case
        fidelity = QuantumMath.estimate_quantum_fidelity({}, "00")
        assert fidelity == 0.0

    def test_calculate_success_probability(self):
        """Test success probability calculation"""
        prob = QuantumMath.calculate_success_probability(1, 4)
        assert 0 <= prob <= 1

        # Test edge case
        prob = QuantumMath.calculate_success_probability(1, 1)
        assert prob == 1.0


class TestPerformanceOptimizer:
    """Test performance optimization utilities"""

    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        optimizer = PerformanceOptimizer()
        assert hasattr(optimizer, "performance_data")
        assert hasattr(optimizer, "logger")

    def test_monitor_execution(self):
        """Test execution monitoring"""
        optimizer = PerformanceOptimizer()

        def test_function():
            return "success"

        metrics = optimizer.monitor_execution("test_alg", test_function)

        assert metrics["algorithm"] == "test_alg"
        assert metrics["success"] is True
        assert metrics["result"] == "success"
        assert "execution_time" in metrics
        assert "memory_usage" in metrics

    def test_performance_summary(self):
        """Test performance summary generation"""
        optimizer = PerformanceOptimizer()

        # Monitor some executions
        def dummy_func():
            return True

        optimizer.monitor_execution("test", dummy_func)
        optimizer.monitor_execution("test", dummy_func)

        summary = optimizer.get_performance_summary("test")
        assert summary["algorithm"] == "test"
        assert summary["executions"] == 2
        assert "avg_execution_time" in summary

    def test_optimize_batch_size(self):
        """Test batch size optimization"""
        optimizer = PerformanceOptimizer()

        # Test with no data
        batch_size = optimizer.optimize_batch_size("unknown", 100)
        assert batch_size == 100

        # Test with high memory usage
        optimizer.performance_data["high_mem"] = [{"memory_usage": {"delta_mb": 200}}]
        batch_size = optimizer.optimize_batch_size("high_mem", 100)
        assert batch_size <= 100

    def test_resource_recommendations(self):
        """Test resource recommendations"""
        optimizer = PerformanceOptimizer()

        # Test with no data
        recommendations = optimizer.get_resource_recommendations()
        assert "recommendation" in recommendations

        # Test with some data
        def dummy_func():
            return True

        optimizer.monitor_execution("test", dummy_func)
        recommendations = optimizer.get_resource_recommendations()
        assert "avg_memory_mb" in recommendations
        assert "recommendations" in recommendations
