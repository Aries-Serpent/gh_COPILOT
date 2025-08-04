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

## Workflow Integration

1. Generate templates using the unified script generation utility. The
   utility now classifies templates by clustering placeholder counts
   (KMeans) and records the mapping in ``cluster_output.json``.
2. Regenerate or create new templates with ``CompleteTemplateGenerator``.
   When template metadata becomes stale, call
   ``cleanup_legacy_assets()`` to purge records older than your
   retention window.
3. After generation and cleanup, run ``AutonomousFileManager`` as shown
   above to organize files in the workspace based on the latest
   database state.
