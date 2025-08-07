"""Executive dashboard aggregating analytics."""

from typing import Dict

from .technical_dashboard import get_metrics as get_technical_metrics
from .security_dashboard import get_metrics as get_security_metrics
from .quantum_dashboard import get_metrics as get_quantum_metrics


def collect_analytics() -> Dict[str, Dict]:
    """Collect analytics from all sub dashboards."""
    return {
        "technical": get_technical_metrics(),
        "security": get_security_metrics(),
        "quantum": get_quantum_metrics(),
    }


__all__ = ["collect_analytics"]

