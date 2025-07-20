# Repository Guidelines

This project uses a single `AGENTS.md` at the repository root as the authoritative guide for all contributors. Any older guides are archived under `_MANUAL_DELETE_FOLDER/`.

## Environment Setup

Run `bash setup.sh` after cloning to create a virtual environment and install dependencies. Activate it with `source .venv/bin/activate` and set `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT` as described in `AGENTS.md`.

## Log Maintenance

Empty log files in `logs/` can cause CI failures. The script `scripts/check_zero_logs.sh` verifies that no zero-byte logs are committed. It runs in CI and should also be executed locally before opening a pull request:

```bash
bash scripts/check_zero_logs.sh
```

Any zero-size files should be removed or quarantined using `scripts/maintenance/quarantine_zero_byte_logs.py`.

