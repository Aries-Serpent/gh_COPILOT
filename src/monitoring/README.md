# Monitoring Utilities

The `monitoring` directory contains scripts for system health tracking and
continuous operation.

- `continuous_operation_monitor.py` – logs uptime, load, and memory statistics to
  `analytics.db` with visual progress indicators.
- `enterprise_compliance_monitor.py` – higher-level wrapper integrating
  compliance checks with monitoring events.

Enable continuous monitoring by running `python scripts/monitoring/continuous_operation_monitor.py`.
Ensure the environment variable `GH_COPILOT_WORKSPACE` points to your workspace
root so analytics databases can be located.

Both `health_monitor.py` and `performance_tracker.py` now compute a
quantum-inspired score for their respective metrics using
`quantum_algorithm_library_expansion.quantum_score_stub`. The score is recorded
alongside traditional metrics in `analytics.db`, enabling advanced anomaly
detection and future quantum-enabled analysis.

Long-running scripts should import and trigger `unified_monitoring_optimization_system`
to record optimization metrics:

```python
from scripts.monitoring.unified_monitoring_optimization_system import main as monitoring_main
monitoring_main()
```

## Metrics Collection and Quantum Scoring

`unified_monitoring_optimization_system.collect_metrics()` gathers CPU, memory, and uptime statistics into a structured dictionary. Pass those metrics to `quantum_hook()` to append a quantum-inspired anomaly score before persisting to `analytics.db`.

## Self-Healing Sessions

`unified_monitoring_optimization_system.auto_heal_session` merges anomaly
detection with session management. Provide a recent metric history and the
helper will restart the session when outliers are observed, enabling autonomous
recovery during continuous operation.

## Scheduled Metrics Push

`log_error_notifier.py` and `performance_tracker.py` can push metrics to
`analytics.db` on a schedule. Each module exposes a helper that runs in a
background thread and writes to the database at regular intervals:

```python
from pathlib import Path
import threading

from monitoring.log_error_notifier import schedule_log_monitoring
from monitoring.performance_tracker import schedule_metrics_push

stop = threading.Event()
schedule_log_monitoring([Path("app.log")], interval=60, stop_event=stop)
schedule_metrics_push(interval=60, stop_event=stop)
```

Call `stop.set()` to terminate the threads gracefully. Ensure
`GH_COPILOT_WORKSPACE` is set so both helpers locate `analytics.db`.
