
# Analytics Logging Integration — 2025-08-19T022606Z

## What changed
- Added `src/gh_copilot/analytics_logger.py` with:
  - `log_event(level, event, details, *, db_path=None, test_mode=None)`
  - `log_sync_operation(file_path, count, status, *, db_path=None, test_mode=None)`
  - TEST_MODE policy: in-memory DB unless `ANALYTICS_DB_PATH` is set.
- Tests:
  - `tests/test_analytics_logging.py` (3 tests)
- README updated: ensured "Analytics Database" section and removed dangling "()".
- Created sample HAR at `tests/data_sample.har` (2 fake entries).

## Mapping & Rationale
- Followed README's events schema; avoided hard-binding to unknown CLI commands.
- No GitHub Actions files touched.

## Open gaps
- If CLI exists with a known command to process HARs, wire `log_sync_operation(...)` into that path.
- Consider adding `level` taxonomy and more tables if needed (out of scope).

