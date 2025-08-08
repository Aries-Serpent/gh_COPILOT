# Session Wrapper

`session_wrapper.sh` wraps arbitrary commands with the help of
`tools/shell_buffer_manager.sh` to guard against long line overflows.
Each invocation stores metadata and chunked output under
`$HOME/.gh_copilot_sessions/<session_id>/`.

## Environment variables

| Variable | Description |
| --- | --- |
| `SESSION_WRAPPER_ROOT` | Optional override for the session storage directory. Default: `$HOME/.gh_copilot_sessions`. |
| `SESSION_WRAPPER_CHUNK_SIZE` | Maximum size in bytes for each output chunk file. Default: `100000`. |
| `SESSION_WRAPPER_MAX_LINE_LENGTH` | Line length forwarded to `shell_buffer_manager.sh` to cap individual line length. Default: `1550`. |

## Usage

### Wrap a command

```bash
bash .github/scripts/session_wrapper.sh wrap "echo hello"
```

The command output is written to chunk files and the session ID is printed
to stdout.

### Recover a session

```bash
bash .github/scripts/session_wrapper.sh recover <session_id>
```

`recover` prints the stored metadata followed by the replayed chunk
contents, enabling audits or debugging in GitHub Actions workflows.

