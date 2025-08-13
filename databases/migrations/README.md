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
18. `add_version_to_documentation_assets.sql`
19. `add_violation_logs.sql`
20. `create_todo_fixme_tracking.sql`
21. `extend_todo_fixme_tracking.sql`

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

An accompanying Graphviz file at `docs/diagrams/migration_dependencies.dot` visualizes
these relationships. For entity-relationship diagrams of the databases, see
[docs/ER_DIAGRAMS.md](../../docs/ER_DIAGRAMS.md).

## Migration Prerequisites

The following table lists any prerequisites for each migration and the related
rollback step. Most migrations simply create a new table and can be reverted by
restoring a database backup.

| Migration | Prerequisites | Rollback |
|-----------|---------------|----------|
| `add_audit_log.sql` | None | Restore backup or drop `audit_log` |
| `add_code_audit_history.sql` | None | Drop `code_audit_history` |
| `add_code_audit_log.sql` | None | Drop `code_audit_log` |
| `add_correction_history.sql` | None | Drop `correction_history` |
| `add_correction_logs.sql` | None | Drop `correction_logs` |
| `add_corrections.sql` | None | Drop `corrections` |
| `add_cross_link_events.sql` | None | Drop `cross_link_events` |
| `add_cross_link_suggestions.sql` | None | Drop `cross_link_suggestions` |
| `add_cross_link_summary.sql` | None | Drop `cross_link_summary` |
| `add_dashboard_alerts.sql` | None | Drop `dashboard_alerts` |
| `add_placeholder_removals.sql` | None | Drop `placeholder_removals` |
| `add_rollback_failures.sql` | None | Drop `rollback_failures` |
| `add_rollback_logs.sql` | None | Drop `rollback_logs` |
| `add_rollback_strategy_history.sql` | None | Drop `rollback_strategy_history` |
| `add_size_violations.sql` | None | Drop `size_violations` |
| `add_sync_events_log.sql` | None | Drop `sync_events_log` |
| `add_unified_wrapup_sessions.sql` | None | Drop `unified_wrapup_sessions` |
| `add_version_to_documentation_assets.sql` | None | Restore backup |
| `add_violation_logs.sql` | None | Drop `violation_logs` |
| `create_todo_fixme_tracking.sql` | `add_placeholder_removals.sql` | Drop `todo_fixme_tracking` |
| `extend_todo_fixme_tracking.sql` | `create_todo_fixme_tracking.sql` | Remove added columns |

## Sample Commands

Run all migrations at once:

```bash
python scripts/run_migrations.py
```

Expected log snippet on success:

```
[INFO] applying add_audit_log.sql
[INFO] applying add_code_audit_history.sql
...
[INFO] applying extend_todo_fixme_tracking.sql
```

If a migration fails you may see output like:

```
sqlite3.OperationalError: table violation_logs already exists
```

In that case restore the database from the last known good backup and rerun the
migration script.

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
- `code_audit_log` is created exclusively by `add_code_audit_log.sql`; the unified database initializer no longer defines this table.
- For compliance details see `scripts/database/add_code_audit_log.py`.
- Audit logging is integrated via `scripts/code_placeholder_audit.py`.
- You can apply all migrations at once by running `python scripts/run_migrations.py`.

---
