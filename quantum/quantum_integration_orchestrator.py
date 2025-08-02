"""High-level orchestration for quantum algorithm execution.

Provides a simple interface that coordinates the algorithm registry and
executor. When quantum hardware is unavailable, the underlying executor
falls back to the local `qasm_simulator` so callers can rely on a
consistent API.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .orchestration.executor import QuantumExecutor
from .orchestration.registry import get_global_registry
from .hybrid_database_processor import QuantumDatabaseProcessor
from .next_generation_ai import NextGenerationAI
from .quantum_data_pipeline import QuantumDataPipeline


class QuantumIntegrationOrchestrator:
    """Coordinate execution of registered quantum algorithms."""

    def __init__(
        self,
        *,
        use_hardware: bool = False,
        backend_name: Optional[str] = None,
        max_workers: int = 4,
    ) -> None:
        self.executor = QuantumExecutor(
            max_workers=max_workers,
            use_hardware=use_hardware,
            backend_name=backend_name,
        )
        self.registry = get_global_registry()

    # ------------------------------------------------------------------
    # Advanced algorithm and database-processing helpers
    # ------------------------------------------------------------------

    def analyze_data(self, data: Iterable[float]) -> Dict[str, Any]:
        """Run next-generation AI analysis on ``data``.

        The method selects between quantum and classical strategies based on
        whether the underlying executor reports hardware availability.
        """

        ai = NextGenerationAI(use_quantum=self.executor.use_hardware)
        return ai.analyze(data)

    def process_database(
        self, query: str, *, use_quantum: bool = True
    ) -> Dict[str, Any]:
        """Process a database query with optional quantum acceleration."""

        processor = QuantumDatabaseProcessor(
            use_quantum=use_quantum,
            hardware_available=self.executor.use_hardware,
        )
        return processor.process(query)

    def run_algorithm(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a single algorithm by name."""
        return self.executor.execute_algorithm(name, **kwargs)

    def run_plan(
        self, algorithm_configs: List[Dict[str, Any]], *, parallel: bool = False
    ) -> List[Dict[str, Any]]:
        """Execute multiple algorithms sequentially or in parallel."""
        if parallel:
            return self.executor.execute_algorithms_parallel(algorithm_configs)
        return self.executor.execute_algorithms_sequential(algorithm_configs)

    def available_algorithms(self) -> List[str]:
        """List algorithms registered with the global registry."""
        return self.registry.list_algorithms()

    def execution_summary(self) -> Dict[str, Any]:
        """Return aggregated statistics from the executor."""
        return self.executor.get_execution_summary()

    def run_data_pipeline(
        self,
        db_path: str | None = None,
        *,
        use_hardware: bool | None = None,
    ) -> Dict[str, Any]:
        """Execute the quantum-accelerated data pipeline."""

        pipeline = QuantumDataPipeline(
            use_hardware=use_hardware if use_hardware is not None else self.executor.use_hardware,
            backend_name=self.executor.backend_name,
        )
        return pipeline.run(db_path=db_path)


__all__ = ["QuantumIntegrationOrchestrator"]
