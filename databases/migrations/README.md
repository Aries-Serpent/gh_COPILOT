# Database Migrations Guide

## Migration Files & Order
- `add_code_audit_log.sql`: Adds `code_audit_log` table.
- `add_correction_history.sql`: Adds `correction_history` table (idempotent).
- `add_code_audit_history.sql`: Adds `code_audit_history` table for tracking audit events.
- `add_violation_logs.sql`: Adds `violation_logs` table for compliance issues.
- `add_rollback_logs.sql`: Adds `rollback_logs` table recording restorations.

## Applying Migrations
Run each migration using:
```bash
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_code_audit_history.sql
sqlite3 databases/analytics.db < databases/migrations/add_violation_logs.sql
sqlite3 databases/analytics.db < databases/migrations/add_rollback_logs.sql
```

## Notes
- All migrations are idempotent and safe to re-run.
- For compliance details see `scripts/database/add_code_audit_log.py`.
- Audit logging is integrated via `scripts/code_placeholder_audit.py`.

---
