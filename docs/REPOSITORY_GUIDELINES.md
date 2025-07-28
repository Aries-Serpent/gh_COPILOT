# Repository Guidelines
> Generated: 2025-07-24 19:32:14 | Author: mbaetiong

## OBJECTIVE

This file defines the standard operating procedures (SOPs) for contributing to the **gh_COPILOT** project, maintaining repository health, and ensuring compliance with enterprise and team guidelines.

## AGENTS RESPONSIBILITY

This project uses a **single source of truth** for contributor guidelines: `AGENTS.md`, located at the repository root. A synchronized backup copy is also maintained at `.github/instructions/AGENTS.md`. Contributors are responsible for reviewing the latest version before initiating PRs or updates.

Note: Any obsolete or deprecated guidelines are moved to an archival location `archives/`.

---

## ENVIRONMENT SETUP

Developers must initialize the project environment properly to maintain consistent development workflows. Follow these steps:

### 1. Clone Repository
Clone the `gh_COPILOT` repository to your local machine.

```bash
git clone https://github.com/Aries-Serpent/gh_COPILOT.git
cd gh_COPILOT
```

### 2. Run Initialization Script
Run the included initialization script to create a virtual environment, install dependencies, and set default configuration files.

```bash
bash setup.sh
```

### 3. Virtual Environment Activation
Activate the Python virtual environment that was created by the setup script.

```bash
source .venv/bin/activate
```

### 4. Workspace and Backup Variables
Set the following environment variables in your shell configuration (or load them dynamically using `.env` files):
- **`GH_COPILOT_WORKSPACE`:** Specifies the repository workspace.
- **`GH_COPILOT_BACKUP_ROOT`:** Ensures backups and logs are stored outside the workspace to prevent recursive violations. If unset, the system defaults to `/tmp/<user>/gh_COPILOT_Backups` on Linux.
- **`CLW_MAX_LINE_LENGTH`:** Optional terminal output wrap length. Set to `1550` to avoid exceeding the 1600-byte console limit when using `clw`.
- **`API_SECRET_KEY`:** Secret used by the Enterprise API. Set this or provide `api_secret_key` in your config file.

Example:

```bash
export GH_COPILOT_WORKSPACE=$(pwd)
export GH_COPILOT_BACKUP_ROOT=/external_path/backups/
```

Configurations should follow the standards outlined in `AGENTS.md`.

### WLC Session Manager and Database Tracking
The script `scripts/wlc_session_manager.py` implements the Wrapping, Logging,
and Compliance (WLC) methodology. When executed, it logs session metadata and a
compliance score into the `unified_wrapup_sessions` table of `production.db`.
Ensure `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT` are set before running:

```bash
export GH_COPILOT_WORKSPACE=$(pwd)
export GH_COPILOT_BACKUP_ROOT=/path/to/backups
python scripts/wlc_session_manager.py --steps 2 --db-path databases/production.db --verbose
```

Use `/usr/local/bin/clw` when reviewing output to avoid long terminal lines.
Add `CLW_MAX_LINE_LENGTH=1550` to your environment (or `.env`) to keep wrapped
output under the 1600-byte limit, and pipe large output through `clw`.

The test `tests/test_wlc_session_manager.py` verifies that a new session record
is inserted and logs are written under `$GH_COPILOT_BACKUP_ROOT/logs/`.

Each entry in `production.db`'s `unified_wrapup_sessions` table captures the
session ID, timestamps, completion status, compliance score, and any error
details, providing an auditable history of WLC runs.
The table includes columns `session_id`, `start_time`, `end_time`, `status`,
`files_organized`, `configs_validated`, `scripts_modularized`,
`root_files_remaining`, `compliance_score`, `validation_results`, and
`error_details`.

---

## WLC Session Logging

Use `scripts/wlc_session_manager.py` to execute tasks under the Wrapping, Logging,
and Compliance methodology. Each run writes a row to the
`production.db` table `unified_wrapup_sessions` capturing the session ID,
start and end times, completion status, compliance score, and any errors.

```bash
python scripts/wlc_session_manager.py --steps 2 --db-path databases/production.db --verbose
```

Log files are stored under `$GH_COPILOT_BACKUP_ROOT/logs/`.

### Output Safety with `clw`
Pipe any command that could produce large output through `/usr/local/bin/clw`
to avoid exceeding the 1600-byte line limit. Example:

```bash
grep -R "pattern" | /usr/local/bin/clw
```

If a limit error occurs, restart the session, rerun `setup.sh`, and repeat the
command with `clw` or redirect the output to a file for chunked review.

---

## LOG MAINTENANCE

To avoid unnecessary CI failures or clutter in Pull Requests, ensure that:
1. **Zero-Byte Logs:** Any log files with zero-byte sizes in `logs/` are removed, moved to quarantine, or filled with placeholders.
2. **Verification Script:** Use the provided script `scripts/check_zero_logs.sh` locally before pushing to verify compliance.

```bash
bash scripts/check_zero_logs.sh
```

If zero-byte files are detected, run `scripts/maintenance/quarantine_zero_byte_logs.py` for automated cleanup or manual quarantining.

---

## TESTING POLICY

Testing is mandatory prior to merge requests. Follow the procedure below before running any tests:
1. Run setup operations:
```bash
bash setup.sh
source .venv/bin/activate
```

2. Run tests with appropriate tools:
```bash
make test   # Preferred test aggregator, combines unit and integration tests
pytest -v   # Alternative for verbose test output
```

---

## ARCHIVAL POLICY

Binary files (e.g., `.zip`, `.7z`, `.tar`) must adhere to the version control archival policy:
1. **Restricted Inclusion:** Only source files (code, documentation) should remain under version control.
2. **Immediate Cleanup:** If binary files are mistakenly included, they should be moved to a cleanup directory outside the repo and `.gitignore` updated:
```bash
grep --exclude=.gitignore "*.zip|*.7z" /.bad_logs_dirs/strict_cleanup_archive) 
 -else assure . not redundantly/git.`pecified-details)" folder:<logical+audit--- Output. Replace/
```

Ensure repository health by iteratively:

Updating global formatting and handling assurance
