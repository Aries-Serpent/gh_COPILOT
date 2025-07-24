# AGENTS Quick Reference

This condensed guide highlights the most critical rules from `AGENTS.md`.

## Setup
- Run `bash setup.sh` and activate the environment with `source .venv/bin/activate`.
- Verify `/usr/local/bin/clw` exists and is executable; recreate it if missing.
- Set `GH_COPILOT_WORKSPACE` to the repo root and `GH_COPILOT_BACKUP_ROOT` to a directory outside the workspace.
- After setup, run `ruff check`, `ruff format`, `pyright`, and `pytest` to ensure the environment is ready.

## Command Usage
- Use only non-interactive shell commands like `cat`, `grep`, and `sed` for file operations.
- Apply code changes via the `apply_patch` tool. Avoid interactive editors and background daemons.
- Do not install extra packages beyond those listed in `requirements*.txt`.

## Output Handling (`clw`)
- Pipe any command with potentially long output through `clw` or capture it to a file and inspect with `head`/`tail`.
- If the terminal reports a line-length error, start a new session, re-run the setup steps, and retry the command using `clw`.

Refer to the root `AGENTS.md` for comprehensive guidelines.
