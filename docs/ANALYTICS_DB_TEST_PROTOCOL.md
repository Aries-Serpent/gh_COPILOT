# Analytics DB Test-Only Protocol

This document describes the procedure for validating the `analytics.db` migrations without automatically creating or modifying the database file. All automation must operate in **test mode** only.

## Manual Migration

Run the following commands manually if `analytics.db` needs the new tables:

```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
```

The database file is not generated automatically. A human operator must execute these commands to create the `code_audit_log` and `correction_history` tables.

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
    ], desc="Simulating migration steps", unit="step"):
        conn.executescript(sql.read_text())
```

No `analytics.db` file is created during testing.

## Visual Processing Indicators

All test scripts log the start time, use a progress bar, and provide status updates to comply with the Visual Processing Indicators standard.

## Dual Copilot Validation

Primary migration logic is verified by a secondary check ensuring both new tables exist before the simulation succeeds.

