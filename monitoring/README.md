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

Long-running scripts should import and trigger `UnifiedMonitoringOptimizationSystem`
to record optimization metrics:

```python
from scripts.monitoring.unified_monitoring_optimization_system import main as monitoring_main
monitoring_main()
```
