# Backup Compliance Guide

This document explains the approved workflow for creating backups, restoring from snapshot archives, and verifying those operations using `disaster_recovery.db`.

## Running Backup Scripts

1. Ensure the environment variables are set:
   ```bash
   export GH_COPILOT_WORKSPACE=/workspace/gh_COPILOT
   export GH_COPILOT_BACKUP_ROOT=/tmp/gh_COPILOT_backup
   ```
   The backup root **must** reside outside the repository to avoid recursion.
2. Run the autonomous backup manager against a target directory:
   ```bash
   python scripts/file_management/autonomous_backup_manager.py /path/to/project
   ```
   Expected output includes a progress bar and a message similar to:
   ```text
   Backing up project [##########] 100% | 24/24 files
   Backup created at /tmp/gh_COPILOT_backup/project
   ```
3. Optionally compress recent backups for archival:
   ```bash
   python scripts/backup_archiver.py
   ```
   A `.7z` archive will appear under `archive/`.

## Restoring from Snapshots

Snapshots are stored as timestamped folders under `$GH_COPILOT_BACKUP_ROOT`. To restore a snapshot:
1. Locate the desired snapshot directory:
   ```bash
   ls $GH_COPILOT_BACKUP_ROOT
   ```
2. Copy the snapshot back to the workspace or another location:
   ```bash
   cp -r $GH_COPILOT_BACKUP_ROOT/project_20250101 /restored/project
   ```
   Verify the files match the snapshot contents before overwriting existing data.

## Verification with `disaster_recovery.db`

Each backup and restore operation is logged in `disaster_recovery.db`. Use the provided verification script:
```bash
python scripts/db_tools/verify_disaster_recovery.py --db databases/disaster_recovery.db
```
Expected output:
```text
✅ Verified 3 backup operations
✅ Verified 2 restore operations
```
The script queries the `backup_operations` table to confirm that backups completed and that corresponding restore entries exist.

---
Ensure all commands are executed from the project root with the virtual environment activated.
