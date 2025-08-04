# External Backup Compliance Guide

## AGENTS.md Compliance

Per AGENTS.md requirements, ALL backups must be stored outside the workspace directory.
For a short summary of these rules, see `.github/instructions/AGENTS_QUICK_REFERENCE.md`.

### Configuration Options

1. **Environment Variable (Recommended)**:
```bash
export GH_COPILOT_BACKUP_ROOT="/external/backup/location"
```

2. Default External Locations:
- Windows: E:/temp/gh_COPILOT_Backups
- Unix/Linux: /temp/gh_COPILOT_Backups

Validation
The system automatically validates that backup locations are external to the workspace and will raise errors if internal backup attempts are detected. The `UnifiedDisasterRecoverySystem` refuses to run when `GH_COPILOT_BACKUP_ROOT` points inside the workspace.

Usage

### Scheduling Backups
The scheduler keeps the most recent five backups by default. Override the
retention by passing ``max_backups``.

```python
from unified_disaster_recovery_system import schedule_backups

backup_path = schedule_backups()  # retains up to 5 backups
```

### Restoring a Backup
``restore_backup`` validates that the file resides under
``$GH_COPILOT_BACKUP_ROOT`` and outside the workspace before restoring it.

```python
from unified_disaster_recovery_system import restore_backup

restore_backup(backup_path)
```

### Disaster Recovery
Use `UnifiedDisasterRecoverySystem` to restore files from external backups:
```python
from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem

system = UnifiedDisasterRecoverySystem()
system.perform_recovery()
```
The utility copies data from `$GH_COPILOT_BACKUP_ROOT/production_backup` into a `restored/` directory and logs `[START]` and `[SUCCESS]` indicators. Recovery aborts if the backup root is inside the workspace.

Both scheduling and restore operations record compliance events through the built-in `ComplianceLogger` for auditing.

Advanced users may directly configure helpers:

```python
from unified_disaster_recovery_system import (
    get_backup_scheduler, get_restore_executor, get_compliance_logger,
)

logger = get_compliance_logger()
scheduler = get_backup_scheduler(logger=logger)
executor = get_restore_executor(logger=logger)
```

### Appendix: Using `validate_enterprise_operation()`
Before any script performs file changes, call:
```python
from enterprise_modules.compliance import validate_enterprise_operation

validate_enterprise_operation(path_to_modify)
```
This ensures no backup folders exist inside the workspace and blocks operations in `C:/temp`.
