# Database Migrations Guide

## Migration Files & Order
- `create_todo_fixme_tracking.sql`: Creates the `todo_fixme_tracking` table with
  `status` and `removal_id` columns.
- `add_code_audit_log.sql`: Adds `code_audit_log` table.
- `add_correction_history.sql`: Adds `correction_history` table (idempotent).
- `add_code_audit_history.sql`: Adds `code_audit_history` table for tracking audit events.
- `add_violation_logs.sql`: Adds `violation_logs` table for compliance issues.
- `add_rollback_logs.sql`: Adds `rollback_logs` table recording restorations.
- `add_corrections.sql`: Adds `corrections` table used for compliance metrics.
- `add_placeholder_removals.sql`: Adds `placeholder_removals` table for tracking removed placeholders.
- `add_size_violations.sql`: Adds `size_violations` table tracking database size breaches.
- `add_unified_wrapup_sessions.sql`: Adds `unified_wrapup_sessions` table used
  by wrap-up orchestrators.
- `add_placeholder_removals.sql`: Adds `placeholder_removals` table used when
  tracking cleanup actions.
- `add_size_violations.sql`: Adds `size_violations` table used by size
  monitoring utilities.
- `extend_todo_fixme_tracking.sql`: Adds `status` and `removal_id` columns linking to `placeholder_removals`.
- `add_placeholder_removals.sql`: Creates `placeholder_removals` table for cleanup tracking.
- `add_size_violations.sql`: Creates `size_violations` table for database size checks.

## Applying Migrations
Run each migration using:
```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_violation_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_rollback_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_corrections.sql
sqlite3 databases/analytics.db < databases/migrations/add_placeholder_removals.sql
sqlite3 databases/analytics.db < databases/migrations/add_size_violations.sql
sqlite3 databases/analytics.db < databases/migrations/add_unified_wrapup_sessions.sql
sqlite3 databases/analytics.db < databases/migrations/add_placeholder_removals.sql
sqlite3 databases/analytics.db < databases/migrations/add_size_violations.sql
sqlite3 databases/analytics.db < databases/migrations/create_todo_fixme_tracking.sql
sqlite3 databases/analytics.db < databases/migrations/extend_todo_fixme_tracking.sql
sqlite3 databases/analytics.db < databases/migrations/add_placeholder_removals.sql
sqlite3 databases/analytics.db < databases/migrations/add_size_violations.sql
```

## Notes
- All migrations are idempotent and safe to re-run.
- For compliance details see `scripts/database/add_code_audit_log.py`.
- Audit logging is integrated via `scripts/code_placeholder_audit.py`.
- You can apply all migrations at once by running `python scripts/run_migrations.py`.

---
