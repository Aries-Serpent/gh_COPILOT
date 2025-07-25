# WLC Session Manager

The Wrapping, Logging, and Compliance (WLC) methodology provides a structured approach for session execution.

- **Wrapping**: validates the environment before actions occur.
- **Logging**: records progress and results in `production.db`.
- **Compliance**: tracks enterprise compliance scores and audit details.

This file documents how `scripts/wlc_session_manager.py` implements the WLC methodology with dual-copilot validation and tqdm progress indicators.

## Environment Setup

Ensure the following environment variables are configured before running the session manager:

- `GH_COPILOT_WORKSPACE` – absolute path to the project root.
- `GH_COPILOT_BACKUP_ROOT` – external directory for logs and backups.

Both paths must exist or the tool will raise an `EnvironmentError`.

Set `WLC_RUN_ORCHESTRATOR=1` to execute the `UnifiedWrapUpOrchestrator` after the
session completes.

The script accepts an optional `--db-path` argument to specify an alternate
database, and `--orchestrate` to run the orchestrator inline.

## Example Usage

Run the session manager directly to start a WLC session:

```bash
python scripts/wlc_session_manager.py
```

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
