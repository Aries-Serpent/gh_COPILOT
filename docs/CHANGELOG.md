# Changelog

## [4.1.4] - 2025-07-28
- Documented test-only protocol for `analytics.db` migrations.
- Added `ANALYTICS_DB_TEST_PROTOCOL.md` with manual commands and testing notes.

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

