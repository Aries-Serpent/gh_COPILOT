# Changelog

## [4.1.10] - 2025-08-01
- Updated `STUB_MODULE_STATUS.md` to mark `DBFirstCodeGenerator`,
  `documentation_db_analyzer` and `workflow_enhancer` as incomplete.
- Clarified failing tests in README with explicit module references.
- Documented full test suite execution in CI configuration.

## [4.1.9] - 2025-07-31
- Enforced secondary validation across automation scripts.
- Added aggregation logic to `enterprise_dual_copilot_validator`.
- Documented dual-copilot enforcement in README.

## [4.1.8] - 2025-07-30
- Added documentation update workflow instructions.
- Clarified that quantum modules operate in simulation mode only.
- Noted incomplete modules and failing tests in README and stub summary.

## [4.1.7] - 2025-07-30
- Added analytics logging hooks in `EnterpriseFileRelocationOrchestrator`.
- Fixed timezone import in `tools/automation_setup.py`.
- Updated README statistics and stub status documentation.

## [4.1.6] - 2025-07-29
- Added `_log_event` hooks to `documentation_ingestor` and `automation_setup` scripts.
- Updated tests to reflect simulated analytics logging.
- Clarified quantum integration docs are simulation-only.
- Updated `STUB_MODULE_STATUS.md` to note all modules log to analytics.
- Documented placeholder resolution tracking workflow.
- Updated usage guides with commands to mark corrections and verify via dashboard.

## [4.1.5] - 2025-07-29
- `log_quantum_event` no longer auto-creates `analytics.db`; added test to verify this behavior.

## [4.1.4] - 2025-07-28
- Documented test-only protocol for `analytics.db` migrations.
- Added `ANALYTICS_DB_TEST_PROTOCOL.md` with manual commands and testing notes.
- Added `add_code_audit_history.sql` migration for `code_audit_history` table.
- Added `user_id` column and index to `correction_history` migration.

## [4.1.3] - 2025-07-27
- Verified presence of new session and monitoring modules.
- Refreshed documentation for wrappers and utilities.

## [4.1.2] - 2025-07-26
- Added migration README describing how to apply SQL files.
- Updated `add_code_audit_log.py` wrapper export.
- Made `add_correction_history.sql` idempotent.
- Documentation now references `unified_database_initializer.py`.
- Added instructions for manually applying `add_code_audit_log.sql` if shipped analytics.db lacks the table.

## [4.1.1] - 2025-07-25
- `add_correction_history.sql` made idempotent to preserve data.
- `README.md` now references `unified_database_initializer.py`.

## [4.1.0] - 2025-07-24
- Initial 4.1 release with session and quantum wrappers.
- Introduced `continuous_operation_monitor` and analytics schema updates.
- Maintenance improvements across utilities.

For changes prior to version 4.1.0 see `documentation/CHANGELOG.md` starting with
the [1.0.0] Initial Enterprise Release.

