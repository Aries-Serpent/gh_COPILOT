#!/usr/bin/env python3
import os
import subprocess
import time
from pathlib import Path

from scripts.monitoring.continuous_operation_monitor import ContinuousOperationMonitor


def test_monitor_run(monkeypatch):
    monitor = ContinuousOperationMonitor(monitor_interval=0, log_db="/tmp/test.db", verbose=False)

    call_count = 0

    def fake_sleep(_):
        nonlocal call_count
        call_count += 1
        if call_count > 0:
            raise KeyboardInterrupt

    monkeypatch.setattr("time.sleep", fake_sleep)
    monitor.monitor_loop()


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "monitoring" / "continuous_operation_monitor.py"


def test_log_created(tmp_path: Path, monkeypatch) -> None:
    log_db = tmp_path / "analytics.db"
    env = os.environ.copy()
    env["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    env["GH_COPILOT_WORKSPACE"] = str(Path(__file__).resolve().parents[1])
    proc = subprocess.Popen(
        [
            "python",
            str(SCRIPT),
            "--interval",
            "0",
            "--log-db",
            str(log_db),
            "--quiet",
        ],
        env=env,
    )
    time.sleep(0.5)
    proc.terminate()
    proc.wait(timeout=5)
    assert log_db.exists()
