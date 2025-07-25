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

## Example Usage

Run the session manager directly to start a WLC session:

```bash
python scripts/wlc_session_manager.py
```

Log files will be written under `$GH_COPILOT_BACKUP_ROOT/logs/` and a new row is inserted into the `unified_wrapup_sessions` table of `production.db`.

### Orchestrator Integration

Pass `--orchestrate` to automatically run the `UnifiedWrapUpOrchestrator` after the WLC steps complete:

```bash
python scripts/wlc_session_manager.py --steps 2 --orchestrate
```

The orchestrator consolidates files and validates configuration. All actions are recorded in the same `unified_wrapup_sessions` table.

## Related Tests

The behavior is validated by `tests/test_wlc_session_manager.py`, which verifies session logging and compliance score tracking.
