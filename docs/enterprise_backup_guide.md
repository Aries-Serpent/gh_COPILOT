# Enterprise Backup Guide

This guide describes how to use the data backup feature in the gh_COPILOT toolkit.
The current implementation enforces an external `GH_COPILOT_BACKUP_ROOT` and
verifies restore operations; misconfigured paths abort with an error.

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

### Recommended Frequency

Run automated backups at least once per day and retain the most recent
five archives. The `schedule_backups()` helper respects the
`GH_COPILOT_MAX_BACKUPS` environment variable so older archives are
pruned automatically.

## Programmatic Backups

The `create_external_backup()` helper ensures backups are written outside
`GH_COPILOT_WORKSPACE` and raises an error if the target directory is inside the
repository:

```python
from pathlib import Path
from scripts.database.complete_consolidation_orchestrator import create_external_backup

source = Path("databases/enterprise_assets.db")
backup = create_external_backup(source, "enterprise_backup")
```

Attempting to back up inside the workspace fails:

```python
create_external_backup(source, "invalid", backup_dir=Path("disaster_recovery"))
# RuntimeError: CRITICAL: Backup location inside workspace: ...
```

For more details on advanced options and restoration procedures, see the documentation in `disaster_recovery/`.

## Restore Drills

Regular restore drills validate that backups are usable. To perform a
drill:

1. Create a backup using `schedule_backups()`.
2. Run `restore_backup()` on the generated file.
3. Confirm a `restore_success` event is logged in `analytics.db` and the
   file is copied to the workspace.

Conduct these drills quarterly to ensure operational readiness.
