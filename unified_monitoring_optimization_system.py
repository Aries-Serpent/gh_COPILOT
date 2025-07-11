#!/usr/bin/env python3
"""UnifiedMonitoringOptimizationSystem - gather simple system metrics."""
import logging
from pathlib import Path
import psutil

TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]'
}


class UnifiedMonitoringOptimizationSystem:
    """Collect CPU metrics for demonstration purposes."""

    def __init__(self, workspace_path: str = '.') -> None:
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger(__name__)

    def collect_metrics(self) -> dict:
        """Return basic CPU usage metrics."""
        self.logger.info(f"{TEXT_INDICATORS['start']} Collecting metrics")
        cpu = psutil.cpu_percent(interval=0.1)
        metrics = {'cpu_percent': cpu}
        self.logger.info(
            f"{TEXT_INDICATORS['success']} CPU usage {cpu:.1f}%")
        return metrics
