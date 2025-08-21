"""Scripts package.

Minimal package initializer that ensures the repository's ``src`` directory is
on :data:`sys.path` so modules within ``scripts`` can reliably use absolute
imports without triggering heavy side effects during package import.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(1, str(_SRC))

__all__ = []
