# AGENTS Quick Reference

This file summarizes core guidelines. Refer to `AGENTS.md` at the project root for full details.

## Setup
- Run `bash setup.sh` after cloning.
- Activate the virtual environment with `source .venv/bin/activate`.
- Set `GH_COPILOT_WORKSPACE` to the repo root and `GH_COPILOT_BACKUP_ROOT` outside the repo.

## Allowed Commands
- Use non-interactive tools such as `cat`, `grep`, `sed`, `jq`, or `apply_patch`.
- Avoid interactive editors or background services.
- Do not perform external network calls unless instructed.

## clw Usage
- Ensure `/usr/local/bin/clw` exists and is executable.
- Pipe commands with potentially long output through `clw` to avoid 1600-byte line issues.

For full guidelines see `AGENTS.md` in the repository root.
