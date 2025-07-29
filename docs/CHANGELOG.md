# Changelog

## [4.1.4] - 2025-07-28
- Documented test-only protocol for `analytics.db` migrations.
- Added `ANALYTICS_DB_TEST_PROTOCOL.md` with manual commands and testing notes.
- Added `add_code_audit_history.sql` migration for `code_audit_history` table.

## [4.1.5] - 2025-07-29
- `log_quantum_event` no longer auto-creates `analytics.db`; added test to
  verify this behavior.

## [4.1.6] - 2025-07-29
- Documented placeholder resolution tracking workflow.
- Updated usage guides with commands to mark corrections and verify via dashboard.

## [4.1.3] - 2025-07-27
- Verified presence of new session and monitoring modules.
- Refreshed documentation for wrappers and utilities.

## [4.1.4] - 2025-07-28
- Added `user_id` column and index to `correction_history` migration.

## [4.1.2] - 2025-07-26
- Added migration README describing how to apply SQL files.
- Updated `add_code_audit_log.py` wrapper export.
- Made `add_correction_history.sql` idempotent.
- Documentation now references `unified_database_initializer.py`.
- Added instructions for manually applying `add_code_audit_log.sql` if shipped
  analytics.db lacks the table.

