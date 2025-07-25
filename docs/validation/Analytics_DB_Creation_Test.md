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
```

If these commands complete without error, the migrations succeed. The
database is **not** created automatically during normal operation; a
human must trigger the command to comply with database‑first and
enterprise standards.

