# WorkspaceOptimizer

`WorkspaceOptimizer` archives rarely used files and records optimization metrics.
It reads tracked script information from `production.db` and compresses files
older than one year into `workspace_archive/` under the backup root. Each
archived file is logged to the `workspace_optimization_metrics` table.

## Example
```python
from pathlib import Path
from scripts.file_management.workspace_optimizer import WorkspaceOptimizer

optimizer = WorkspaceOptimizer(Path('databases/production.db'))
optimizer.optimize(Path('workspace'))
```
