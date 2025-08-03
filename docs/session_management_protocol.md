# Session Management Protocol

This protocol defines safeguards for session handling within the gh_COPILOT toolkit.

## Zero-byte File Guard

Use `ensure_no_zero_byte_files(path)` to verify that a workspace is free of zero-byte files both before and after session cleanup. Wrap calls to close out a session within this context manager to prevent residual artifacts.

## Anti-recursion via PID Tracking

`session_management_consolidation_executor.py` records its process identifier in a PID file under the backup root. If an existing PID is detected, execution halts to avoid recursive invocation. The PID file is removed once execution completes.

These measures help maintain session integrity and prevent accidental recursion during consolidation routines.
