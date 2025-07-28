# Using AutonomousFileManager

The `AutonomousFileManager` organizes workspace files by consulting
`production.db`. It reads from `enhanced_script_tracking` and
`functional_components` to determine where files belong. All operations
follow the guidelines in
[AUTONOMOUS_FILE_MANAGEMENT.instructions.md](../.github/instructions/AUTONOMOUS_FILE_MANAGEMENT.instructions.md).

```python
from pathlib import Path
from scripts.file_management.autonomous_file_manager import AutonomousFileManager

manager = AutonomousFileManager(Path('databases/production.db'))
manager.organize_files(Path('workspace'))
```
