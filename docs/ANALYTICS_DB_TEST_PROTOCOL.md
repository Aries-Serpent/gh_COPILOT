# Analytics DB Test-Only Protocol

This document describes the procedure for validating the `analytics.db` migrations without automatically creating or modifying the database file. All automation must operate in **test mode** only.
All modules use the helpers `ensure_tables()` and `insert_event()` from `utils.log_utils` to create tables and record events when manual writes are allowed.

### Quick Manual Creation

If you need to create `analytics.db` yourself, run the following commands from the repository root:

```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_violation_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_rollback_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_model_deployments.sql
sqlite3 databases/analytics.db < databases/migrations/add_violation_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_rollback_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_violation_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_rollback_logs.sql
```

This must be performed manually; automated scripts never generate the file.

## Manual Migration

Run the following commands manually if `analytics.db` needs the new tables:

```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_history.sql
```

The database file is not generated automatically. A human operator must execute these commands to create the `code_audit_log`, `correction_history`, and `code_audit_history` tables.

### Quick Reference: Create `analytics.db`

Run the following commands whenever a real `analytics.db` is required:

```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_history.sql
```

All automated tests run migrations against an in-memory SQLite instance only.

## Testing Guidance

Tests run the migration SQL against an in-memory SQLite instance to confirm the schema applies cleanly. Progress indicators and dual validation ensure compliance.

```python
# Example from tests/test_analytics_migration_simulation.py
from pathlib import Path
import sqlite3
from tqdm import tqdm

with sqlite3.connect(":memory:") as conn:
    for sql in tqdm([
        Path("databases/migrations/add_code_audit_log.sql"),
        Path("databases/migrations/add_correction_history.sql"),
        Path("databases/migrations/add_code_audit_history.sql"),
        Path("databases/migrations/add_violation_logs.sql"),
        Path("databases/migrations/add_rollback_logs.sql"),
        Path("databases/migrations/add_model_deployments.sql"),
    ], desc="Simulating migration steps", unit="step"):
        conn.executescript(sql.read_text())
```

No `analytics.db` file is created during testing.

## Visual Processing Indicators

All test scripts log the start time, use a progress bar, and provide status updates to comply with the Visual Processing Indicators standard.

## Dual Copilot Validation

Primary migration logic is verified by a secondary check ensuring both new tables exist before the simulation succeeds.

