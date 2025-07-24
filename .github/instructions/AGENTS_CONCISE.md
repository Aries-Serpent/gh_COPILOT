# AGENTS Quick Reference

This file summarizes the core rules from the full `AGENTS.md`.

## Environment Setup
- Run `bash setup.sh` before making changes.
- Activate the virtualenv: `source .venv/bin/activate`.
- Set `GH_COPILOT_WORKSPACE` to the repo root and `GH_COPILOT_BACKUP_ROOT` to an external directory.

## `clw` Utility
- Verify `/usr/local/bin/clw` exists and is executable after setup.
- Pipe any potentially large output through `clw` to avoid terminal crashes.

## Command Usage
- Use only non-interactive commands (`cat`, `grep`, `sed`, etc.).
- Avoid interactive editors or commands that require user input.

Refer to the full guide for complete details.
