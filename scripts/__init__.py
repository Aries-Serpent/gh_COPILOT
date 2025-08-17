"""scripts package"""

from pathlib import Path
import sys

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from . import docs_metrics_validator, validate_docs_metrics

__all__ = [
    "docs_metrics_validator",
    "validate_docs_metrics",
]
