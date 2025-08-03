# Recursion Policy

The workspace and backup directories must never contain one another, even through symlinks.

- **No nested workspaces**: the backup root cannot reside inside the workspace and vice versa.
- **Symlink awareness**: symlinks pointing to the workspace or backup directories are treated as violations. Validation walks the workspace and resolves inodes to catch loops.
- **Bidirectional checks**: both workspace and backup trees are scanned with symlink
  resolution to prevent indirect containment (e.g., a link in the backup root
  pointing back to the workspace).
- **Detailed errors**: any violation raises a ``RuntimeError`` that reports the offending paths for quick diagnosis.
- **Explicit validation**: importing the optimizer module performs no filesystem access. Call `validate_workspace()` or pass `validate_workspace=True` to `QuantumOptimizer` when you need these checks.

Example:
```python
from pathlib import Path
from quantum.optimizers.quantum_optimizer import validate_workspace

# Ensures `/data/workspace` and `/backups` are not recursive
ws = Path('/data/workspace')
bk = Path('/backups')
ws.mkdir(exist_ok=True)
bk.mkdir(exist_ok=True)
validate_workspace()

# Violation examples:
# 1. backup nested inside workspace
(ws / 'backup').mkdir(exist_ok=True)
# 2. backup root linking back to workspace
(bk / 'ws_link').symlink_to(ws)
```

## Developer Usage

Use the `anti_recursion_guard` decorator from `utils.validation_utils` to prevent
scripts from invoking themselves recursively. Decorate any entry points that
perform filesystem operations or manage archives:

```python
from utils.validation_utils import anti_recursion_guard

@anti_recursion_guard
def archive_backups() -> Path:
    ...
```

This guard creates a transient lock file so that re-entrant calls raise a
`RuntimeError` instead of causing recursive behaviour.
