# Enterprise Backup Guide

This guide describes how to use the data backup feature in the gh_COPILOT toolkit.

## Prerequisites
- Ensure the `GH_COPILOT_BACKUP_ROOT` environment variable points to an external directory outside the repository workspace. When running the Docker container, map a host folder to `/backup` so the volume persists:
  ```bash
  docker compose up -d -v /host/backups:/backup
  ```
  Backups will then be available on the host under `/host/backups`.
- Run `bash setup.sh` to create the `.venv` and install dependencies.

## Performing a Backup
1. Verify your environment variables:
   ```bash
   echo $GH_COPILOT_BACKUP_ROOT
   ```
   The path **must** be located outside the repository workspace.
2. Execute the backup command:
   ```bash
   python scripts/automation/enhanced_enterprise_continuation_processor_backup.py --source /path/to/data
   ```
3. After backups are created, run the archiver:
   ```bash
   python scripts/backup_archiver.py
   ```
   This compresses all files under `$GH_COPILOT_BACKUP_ROOT` into a `.7z` file
   placed in `archive/` at the repository root.
4. Backups remain stored within `$GH_COPILOT_BACKUP_ROOT` by default.

For more details on advanced options and restoration procedures, see the documentation in `disaster_recovery/`.
