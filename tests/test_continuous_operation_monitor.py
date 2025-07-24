#!/usr/bin/env python3
from scripts.monitoring.continuous_operation_monitor import ContinuousOperationMonitor


def test_monitor_run():
    monitor = ContinuousOperationMonitor(interval=0)
    assert monitor.run() is True
