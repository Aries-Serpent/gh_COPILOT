# Database Synchronization Guide

This guide outlines recovery procedures and common failure modes for the
`DatabaseSynchronizationEngine`.

## Recovery Steps
1. **Stop the process** – invoke `DatabaseSynchronizationEngine.stop_realtime_sync`
   if running in background or terminate the process using the system tools.
2. **Inspect logs** – review `logs/synchronization.log` for entries marked
   `sync_error` or `conflict_skip` to understand what happened.
3. **Validate databases** – open the affected databases with `sqlite3` and
   confirm that tables and row counts match expectations.
4. **Restore if necessary** – retrieve backups from `$GH_COPILOT_BACKUP_ROOT`
   and replace corrupted databases before rerunning synchronization.
5. **Resume synchronization** – once issues are resolved, run the engine again
   to bring databases back into consistency.

## Real-Time Synchronization
`SyncManager` can operate in real time through the `SyncWatcher` utility. The
watcher observes one or more database pairs and triggers a synchronization when
either side changes:

```python
from database_first_synchronization_engine import SyncManager, SyncWatcher

manager = SyncManager()
watcher = SyncWatcher(manager)
watcher.watch_pairs([(db_a, db_b), (db_c, db_d)], policy="last-write-wins")
```

## Conflict Policies
The synchronization engine supports pluggable conflict resolution. Use the
`"last-write-wins"` policy for timestamp-based merges or supply a custom merge
function via `ResolverPolicy` when domain-specific logic is required.

## Failure Modes
- **Schema mismatch** – target databases missing required tables or columns.
  Update the schema mapping or migrate the databases before retrying.
- **Conflict resolution** – rows with newer timestamps in the target are kept
  and the update is skipped. Ensure clocks are synchronized across systems.
- **I/O errors** – disk or permission errors will abort the process. Fix the
  environment and re-run synchronization.
- **Hook failures** – exceptions raised by a custom `log_hook` are logged as
  `log_hook_error` but do not stop synchronization.
