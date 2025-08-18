# Analytics DB Creation Test

This validation ensures that `databases/analytics.db` can be created and
migrated on demand. The file is tracked in the repository for testing
purposes, but new environments may need to recreate it.

## Test‑Only Creation Command

Run the following commands manually from the repository root to verify
that a fresh analytics database can be initialized:

```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_violation_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_rollback_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_model_deployments.sql
```

For a fully compliant dry‑run, execute the in‑memory test which logs the start
time, shows a progress bar, and reports completion. This demonstrates the
migrations without creating the database file:

```bash
python -m pytest tests/test_analytics_migration_simulation.py -q
```

If these commands complete without error, the migrations succeed. The
database is **not** created automatically during normal operation; a
human must trigger the command to comply with database‑first and
enterprise standards.

