# Session Wrapper and Buffer Utilities

This guide explains how to use the `session_wrapper.sh` and
`shell_buffer_manager.sh` scripts to safely execute commands while
respecting Codex terminal limits.

## Wrapping Commands

```
bash .github/scripts/session_wrapper.sh wrap_command "echo hello"
```

The wrapper executes the command through `shell_buffer_manager.sh`, writes
session metadata to `.session_meta/<session_id>.json`, and prints the
session identifier.

## Recovering Sessions

```
bash .github/scripts/session_wrapper.sh recover_session <session_id>
```

This prints the stored metadata, enabling auditing or reruns. Overflow
from long lines is stored under `/tmp/shell_buffer_overflow/`.

