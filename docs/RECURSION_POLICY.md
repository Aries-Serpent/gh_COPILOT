# Recursion Policy

The workspace and backup directories must never contain one another, even through symlinks.

- **No nested workspaces**: the backup root cannot reside inside the workspace and vice versa.
- **Symlink awareness**: symlinks pointing to the workspace or backup directories are treated as violations. Validation walks the workspace and resolves inodes to catch loops.
- **Explicit validation**: importing the optimizer module performs no filesystem access. Call `validate_workspace()` or pass `validate_workspace=True` to `QuantumOptimizer` when you need these checks.

Example:
```python
from pathlib import Path
from quantum.optimizers.quantum_optimizer import validate_workspace

# Ensures `/data/workspace` and `/backups` are not recursive
Path('/data/workspace').mkdir(exist_ok=True)
Path('/backups').mkdir(exist_ok=True)
validate_workspace()
```
