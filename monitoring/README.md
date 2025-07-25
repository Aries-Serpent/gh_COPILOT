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
