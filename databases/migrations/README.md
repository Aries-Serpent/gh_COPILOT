# Database Migrations Guide

## Prerequisites
Before applying migrations, ensure the following:

- `GH_COPILOT_WORKSPACE` points to the repository root.
- SQLite 3 is installed and available on your `PATH`.
- Optional: set `GH_COPILOT_BACKUP_ROOT` to an external directory for backups.


## Migration Files & Order
Migrations are executed alphabetically by `scripts/run_migrations.py`. Apply them
in the following order to satisfy foreign key constraints:

1. `add_audit_log.sql`
2. `add_code_audit_history.sql`
3. `add_code_audit_log.sql`
4. `add_correction_history.sql`
5. `add_correction_logs.sql`
6. `add_corrections.sql`
7. `add_cross_link_events.sql`
8. `add_cross_link_suggestions.sql`
9. `add_cross_link_summary.sql`
10. `add_dashboard_alerts.sql`
11. `add_placeholder_removals.sql`
12. `add_rollback_failures.sql`
13. `add_rollback_logs.sql`
14. `add_rollback_strategy_history.sql`
15. `add_size_violations.sql`
16. `add_sync_events_log.sql`
17. `add_unified_wrapup_sessions.sql`
18. `add_violation_logs.sql`
19. `create_todo_fixme_tracking.sql`
20. `extend_todo_fixme_tracking.sql`

`extend_todo_fixme_tracking.sql` depends on both `create_todo_fixme_tracking.sql`
and `add_placeholder_removals.sql` because it references the `placeholder_removals`
table.

```
add_placeholder_removals.sql
        ↓
create_todo_fixme_tracking.sql
        ↓
extend_todo_fixme_tracking.sql
```

## Applying Migrations
Use the helper script to apply all migrations:

```bash
python scripts/run_migrations.py
```

The script automatically discovers `*.sql` files in this directory and runs them
alphabetically. To run a single migration manually, execute:

```bash
sqlite3 databases/analytics.db < databases/migrations/<migration>.sql
```

## Rollback
If a migration introduces issues, restore the database from a backup and log the
event in `rollback_logs`:

```bash
cp /path/to/backup/analytics.db databases/analytics.db
sqlite3 databases/analytics.db "INSERT INTO rollback_logs (target, backup, timestamp) VALUES ('analytics.db', '/path/to/backup/analytics.db', datetime('now'));"
```

The `_log_rollback` helper in `enterprise_modules.compliance` performs this step
automatically when called by recovery scripts.

## Notes
- All migrations are idempotent and safe to re-run.
- For compliance details see `scripts/database/add_code_audit_log.py`.
- Audit logging is integrated via `scripts/code_placeholder_audit.py`.
- You can apply all migrations at once by running `python scripts/run_migrations.py`.

---
