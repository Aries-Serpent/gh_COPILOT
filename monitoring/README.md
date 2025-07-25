# Monitoring Scripts

Tools for keeping the gh_COPILOT environment healthy.

- **continuous_operation_monitor.py** – Tracks system metrics and logs them to `analytics.db`.
- **health_monitor.py** – Periodic health checks for services.

Run the continuous monitor:
```bash
python scripts/monitoring/continuous_operation_monitor.py --interval 30
```
Ensure `GH_COPILOT_WORKSPACE` is set before running.
