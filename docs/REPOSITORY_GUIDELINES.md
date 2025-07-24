# Repository Guidelines

This project uses a single `AGENTS.md` at the repository root as the authoritative guide for all contributors. A copy is kept at `.github/instructions/AGENTS.md` for reference. Any older guides are archived under `_MANUAL_DELETE_FOLDER/`.

## Environment Setup

Run `bash setup.sh` after cloning to create a virtual environment and install dependencies. Activate it with `source .venv/bin/activate` and set `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT` as described in `AGENTS.md` (or the copy under `.github/instructions`).

## Log Maintenance

Empty log files in `logs/` can cause CI failures. The script `scripts/check_zero_logs.sh` verifies that no zero-byte logs are committed. It runs in CI and should also be executed locally before opening a pull request:

```bash
bash scripts/check_zero_logs.sh
```

Any zero-size files should be removed or quarantined using `scripts/maintenance/quarantine_zero_byte_logs.py`.

## Running Tests

Always initialize the project environment before executing the test suite. Run
`bash setup.sh` and activate the virtual environment prior to invoking `make test`
or `pytest`:

```bash
bash setup.sh
source .venv/bin/activate
```

## Archival Policy

Binary archives such as `*.zip` and `*.7z` should not remain in version control.
If any appear in `archive*/` or `archives/`, move them to `_MANUAL_DELETE_FOLDER/`
for manual removal. Once a HUMAN clears that folder, AGENTS should extend
`.gitignore` to exclude these archive formats.

