# Session Wrapper and Buffer Utilities

This guide explains how to use the `session_wrapper.sh` and
`shell_buffer_manager.sh` scripts to safely execute commands while
respecting Codex terminal limits.

## Wrapping Commands

```bash
safe-run "echo hello"
```

The `safe-run` alias invokes `session_wrapper.sh wrap` through
`shell_buffer_manager.sh`, writes session metadata to
`$HOME/.gh_copilot_sessions/<session_id>.json`, and prints the session
identifier.

## Recovering Sessions

```bash
bash .github/scripts/session_wrapper.sh recover_session <session_id>
```

This prints the stored metadata, enabling auditing or reruns. Overflow
from long lines is stored under `/tmp/shell_buffer_overflow/`.

## Using the Alias

Add the alias to your shell profile (e.g., `.bashrc` or `.zshrc`):

```bash
alias safe-run='session_wrapper.sh wrap'
```

Once set, wrap any command:

```bash
safe-run "ls -al"
```

