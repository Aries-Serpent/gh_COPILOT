# WLC Quickstart

This guide summarizes the steps for running the WLC Session Manager.

1. `bash setup.sh`
2. `source .venv/bin/activate`
3. Set `GH_COPILOT_WORKSPACE` to the repo root and `GH_COPILOT_BACKUP_ROOT` to an external directory.
4. Run `python scripts/wlc_session_manager.py --steps 1 --db-path databases/production.db --verbose`

All output should be piped through `/usr/local/bin/clw` when viewing logs or large files.
