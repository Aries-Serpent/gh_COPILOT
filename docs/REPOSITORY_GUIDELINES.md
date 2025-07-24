# Repository Guidelines

The authoritative agent guide is `AGENTS.md` at the repository root. A copy is also provided under `.github/instructions/AGENTS.md` for convenience. Any older guides are archived under `_MANUAL_DELETE_FOLDER/`.

## Environment Setup

Run `bash setup.sh` after cloning to create a virtual environment and install dependencies. Activate it with `source .venv/bin/activate` and set `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT` as described in `AGENTS.md` (see also `.github/instructions/AGENTS_CORE_RULES.instructions.md` for a short summary).

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

