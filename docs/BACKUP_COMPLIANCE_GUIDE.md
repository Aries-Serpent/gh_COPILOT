# Backup & Compliance Guide

This guide describes how the disaster recovery utilities manage backups and
logging. The functionality lives in
`scripts/utilities/unified_disaster_recovery_system.py` and is exposed through
`UnifiedDisasterRecoverySystem`.

## Environment Variables

| Variable | Description |
| --- | --- |
| `GH_COPILOT_WORKSPACE` | Absolute path to the workspace that may be restored. Defaults to the current directory. |
| `GH_COPILOT_BACKUP_ROOT` | External directory where backups and logs are stored. **Must not** reside inside the workspace. Defaults to `/tmp/gh_COPILOT_Backups`. |

## Logging Behaviour

Operations are recorded through the enterprise logging system with the
following events:

| Event | Trigger |
| --- | --- |
| `backup_scheduled` | A backup file and checksum were created successfully. |
| `backup_failed` | Scheduling aborted (for example, the backup root was inside the workspace). |
| `restore_success` | A backup was restored and the checksum matched. |
| `restore_failed` | Restoration failed due to a missing or mismatched checksum. |

These logs help maintain compliance records for all backup and restore
operations.

