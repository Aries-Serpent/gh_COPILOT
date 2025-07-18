# External Backup Compliance Guide

## AGENTS.md Compliance

Per AGENTS.md requirements, ALL backups must be stored outside the workspace directory.

### Configuration Options

1. **Environment Variable (Recommended)**:
```bash
export GH_COPILOT_BACKUP_ROOT="/external/backup/location"
```

2. Default External Locations:
- Windows: E:/temp/gh_COPILOT_Backups
- Unix/Linux: /temp/gh_COPILOT_Backups

Validation
The system automatically validates that backup locations are external to the workspace and will raise errors if internal backup attempts are detected.

Usage
```python
from scripts.database.complete_consolidation_orchestrator import create_external_backup
backup_path = create_external_backup(source_file, "my_backup")
```
