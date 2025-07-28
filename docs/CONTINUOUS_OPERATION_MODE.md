# Continuous Operation Mode

The toolkit can run in a fully automated mode to ensure 24/7 monitoring and self‑healing.
The new scheduler integrates the self‑healing system and operation monitor.

## Running the Scheduler

```bash
python scripts/automation/system_maintenance_scheduler.py --interval 60
```

- `--interval` specifies minutes between maintenance cycles.
- Each cycle runs the self‑healing logic and logs a health snapshot.
- Job history is stored in `analytics.db` table `system_maintenance_jobs`.
- Session entries are recorded in `production.db` via `unified_wrapup_sessions`.

Ensure `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT` are set before launching.
The scheduler runs indefinitely and should be used for continuous environments.
