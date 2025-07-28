"""Continuous monitoring engine with periodic health checks."""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Iterable

from tqdm import tqdm

__all__ = ["ContinuousMonitoringEngine"]


class ContinuousMonitoringEngine:
    """Perform continuous health checks with a monitoring cycle."""

    def __init__(self, cycle_seconds: int = 0) -> None:
        self.cycle_seconds = cycle_seconds
        self.logger = logging.getLogger(__name__)

    def run_cycle(self, actions: Iterable[callable] | None = None) -> None:
        """Run a single monitoring cycle."""
        self.logger.info("Cycle start %s", datetime.now().isoformat())
        actions = actions or []
        with tqdm(actions, desc="Monitoring actions", unit="action") as bar:
            for callback in bar:
                callback()
        if actions:
            time.sleep(self.cycle_seconds)
        self.logger.info("Cycle complete")
