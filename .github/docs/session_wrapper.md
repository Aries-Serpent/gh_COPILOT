# Session Wrapper

The repository provides a helper script at `.github/scripts/session_wrapper.sh` for preserving command sessions.

## Usage

```bash
# Initialize the session metadata directory
.github/scripts/session_wrapper.sh setup_session_preservation

# Run a command and capture its session id
session_id=$(.github/scripts/session_wrapper.sh wrap_command "ls -al")

# Recover metadata for a previous session
.github/scripts/session_wrapper.sh recover_session "$session_id"
```

Session metadata and command logs are stored under `~/.gh_copilot_sessions`.
