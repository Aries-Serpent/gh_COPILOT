"""Continuous monitoring engine with periodic health checks."""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable
import argparse
import sqlite3

import psutil
from tqdm import tqdm

from scripts.optimization.automated_optimization_engine import (
    AutomatedOptimizationEngine,
)
from scripts.optimization.intelligence_gathering_system import (
    IntelligenceGatheringSystem,
)
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator

__all__ = ["ContinuousMonitoringEngine", "parse_args", "main"]


class ContinuousMonitoringEngine:
    """Perform continuous health checks with a monitoring cycle."""

    def __init__(
        self,
        cycle_seconds: int = 300,
        *,
        workspace: Path | None = None,
        db_path: Path | None = None,
    ) -> None:
        self.cycle_seconds = cycle_seconds
        self.logger = logging.getLogger(__name__)

        self.workspace = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", "."))
        prod_db = db_path or self.workspace / "databases" / "production.db"

        self.optimizer = AutomatedOptimizationEngine()
        self.intel = IntelligenceGatheringSystem(Path(prod_db))

    @staticmethod
    def _calculate_etc(start_ts: float, current: int, total: int) -> str:
        """Estimate remaining time for progress reporting."""
        if current <= 0:
            return "N/A"
        elapsed = time.time() - start_ts
        total_est = elapsed / (current / total)
        remaining = max(0.0, total_est - elapsed)
        return f"{remaining:.2f}s"

    def _health_check(self) -> dict[str, float | str | int]:
        """Collect basic health metrics."""
        metrics: dict[str, float | str | int] = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "anomaly": 0,
            "note": "",
        }
        try:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            if metrics["cpu_percent"] > 90 or metrics["memory_percent"] > 90:
                metrics["anomaly"] = 1
                metrics["note"] = "High load"
        except OSError as exc:  # pragma: no cover - psutil may not be present
            metrics["anomaly"] = 1
            metrics["note"] = str(exc)
            self.logger.exception("Health check failed")
        return metrics

    def run_cycle(self, actions: Iterable[Callable] | None = None) -> None:
        """Run a single monitoring cycle."""
        start_ts = time.time()
        self.logger.info("Cycle start %s", datetime.now().isoformat())

        steps = list(actions or [])
        total_steps = len(steps) + 1  # include health check

        with tqdm(total=total_steps, desc="Monitoring cycle", unit="step") as bar:
            for cb in steps:
                cb()
                bar.update(1)
                etc = self._calculate_etc(start_ts, bar.n, total_steps)
                bar.set_postfix(ETC=etc)

            metrics = self._health_check()
            bar.update(1)
            etc = self._calculate_etc(start_ts, bar.n, total_steps)
            bar.set_postfix(ETC=etc)

        self.logger.info("Health metrics: %s", metrics)
        if metrics.get("anomaly"):
            self.logger.warning("Anomaly detected: %s", metrics.get("note"))
            try:
                self.optimizer.optimize(self.workspace)
                self.intel.gather()
            except (OSError, sqlite3.Error) as exc:  # pragma: no cover - log only
                self.logger.exception("Auto-remediation failed: %s", exc)

        elapsed = time.time() - start_ts
        etc = self._calculate_etc(start_ts, total_steps, total_steps)
        self.logger.info("Cycle complete in %.2fs | ETC: %s", elapsed, etc)

        if self.cycle_seconds:
            time.sleep(self.cycle_seconds)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run continuous monitoring")
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of monitoring cycles to execute",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Seconds to wait between cycles",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    engine = ContinuousMonitoringEngine(cycle_seconds=ns.interval)
    orchestrator = DualCopilotOrchestrator()
    for _ in range(ns.cycles):
        orchestrator.run(lambda: (engine.run_cycle([]) or True), [])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
