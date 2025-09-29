# WLC Session Manager

The Wrapping, Logging, and Compliance (WLC) methodology provides a structured approach for session execution.

- **Wrapping**: validates the environment before actions occur.
- **Logging**: records progress and results in `production.db`.
- **Compliance**: tracks enterprise compliance scores and audit details.

This file documents how `scripts/wlc_session_manager.py` implements the WLC methodology with dual-copilot validation and tqdm progress indicators.

## Enhanced Session Integrity

- Lifecycle states are logged at the start and end of each session.
- The session manager detects zero-byte files before and after cleanup using `ensure_no_zero_byte_files`.
- Critical lifecycle functions are protected by `anti_recursion_guard` to prevent recursive execution.

## Environment Setup

Ensure the following environment variables are configured before running the session manager:

- `GH_COPILOT_WORKSPACE` – absolute path to the project root.
- `GH_COPILOT_BACKUP_ROOT` – external directory for logs and backups.
- `TEST_MODE` – when set to any value, the session manager exits immediately, skipping logging, delays, and database writes. This is useful for tests.

Both paths must exist or the tool will raise an `EnvironmentError`.

Set `WLC_RUN_ORCHESTRATOR=1` to execute the `UnifiedWrapUpOrchestrator` after the
session completes.

The script accepts an optional `--db-path` argument to specify an alternate
database, and `--orchestrate` to run the orchestrator inline.

### Session Integrity

`unified_session_management_system.py` wraps session startup and cleanup within
`ensure_no_zero_byte_files(path)` to verify that the workspace is free of
zero-byte files both before and after wrap-up. The module also exposes a
`prevent_recursion` decorator that guards against recursive invocations of the
session workflow. Any attempt to re-enter the session logic from the same
process raises a `RuntimeError`.

### NDJSON Example

In addition to database logging, automation steps can append metrics to an NDJSON stream.

```python
from gh_copilot.automation.logging import append_ndjson
append_ndjson('.codex/action_log.ndjson', {'event': 'wlc_wrapup', 'status': 'ok'})
```

This file can be tailed locally or ingested by a dashboard reader.

## Example Usage

Run the session manager directly to start a WLC session with explicit CLI parameters:

```bash
python scripts/wlc_session_manager.py --steps 2 --db-path databases/production.db --verbose
```

### Full Example

Configure your environment and run the session manager in one sequence:

```bash
export GH_COPILOT_WORKSPACE=$(pwd)
export GH_COPILOT_BACKUP_ROOT=/path/to/backups
export API_SECRET_KEY=<generated_secret>
python scripts/wlc_session_manager.py --steps 2 --db-path databases/production.db --orchestrate --verbose
```

This command writes a log file to `$GH_COPILOT_BACKUP_ROOT/logs/` with a timestamped name such as `wlc_20250101_120000.log`.
It also inserts a new row into the `unified_wrapup_sessions` table of `production.db` capturing the session ID, start and end times, status, and compliance score.

For any major workflow, end with the session manager to capture compliance data:

```bash
python my_long_running_script.py
python scripts/wlc_session_manager.py --db-path databases/production.db
```

Logs are saved under `$GH_COPILOT_BACKUP_ROOT/logs/` with a timestamped filename
like `wlc_20250101_120000.log`.

Log files will be written under `$GH_COPILOT_BACKUP_ROOT/logs/` and a new row is inserted into the `unified_wrapup_sessions` table of `production.db`.

The WLC session manager is also invoked automatically by the
`UnifiedWrapUpOrchestrator` to record wrap-up operations. When the orchestrator
finishes its workflow, it triggers a lightweight WLC session using the same
database for compliance tracking.
Each session creates an entry in the `unified_wrapup_sessions` table with
`session_id`, timestamps, status, and a compliance score. Errors are recorded in
the `error_details` column for audit purposes.
All output from subprocess calls should be piped through `/usr/local/bin/clw`
when viewing or storing to ensure no terminal overflow occurs.

## Related Tests

The behavior is validated by `tests/test_wlc_session_manager.py`, which verifies session logging and compliance score tracking.
