# RECLONE_REPO Utility Guide

The `scripts/reclone_repo.py` script restores a clean working copy of a Git repository. Use it when a local clone becomes corrupted or when a fresh copy is required for disaster recovery.

## Requirements
- Python 3.8+
- `git` installed and available on `PATH`
- Parent directory for the destination path must already exist

### Optional Backup
If `--backup-existing` is supplied and the destination directory exists, the script moves the directory to a timestamped backup within `GH_COPILOT_BACKUP_ROOT`.

Set the environment variable to an external path before running:

```bash
export GH_COPILOT_BACKUP_ROOT=/path/to/external/backups
```

The backup root must exist and be outside the destination directory.

### Clean Removal
Use `--clean` to remove an existing destination directory before cloning. This flag is ignored if `--backup-existing` is provided.

## Usage
```bash
python scripts/reclone_repo.py --repo-url https://github.com/example/project.git \
    --dest /tmp/project-clean --branch main --backup-existing
```

On success the script prints the latest commit hash from the new clone.

## Exit Codes
- `0`: clone succeeded
- non-zero: an error occurred (message printed to stderr)
