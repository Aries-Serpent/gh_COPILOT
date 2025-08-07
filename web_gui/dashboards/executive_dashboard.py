"""Executive dashboard aggregating analytics."""

from pathlib import Path
from typing import Dict, Optional

from .technical_dashboard import get_metrics as get_technical_metrics
from .security_dashboard import get_metrics as get_security_metrics
from .quantum_dashboard import get_metrics as get_quantum_metrics
from web_gui.monitoring.alerting import NOTIFICATION_LOG


def collect_analytics(db_path: Optional[Path] = None) -> Dict[str, Dict]:
    """Collect analytics from all sub dashboards.

    ``db_path`` allows overriding the analytics database used by sub dashboards.
    """
    data = {
        "technical": get_technical_metrics(db_path) if db_path else get_technical_metrics(),
        "security": get_security_metrics(db_path) if db_path else get_security_metrics(),
        "quantum": get_quantum_metrics(db_path) if db_path else get_quantum_metrics(),
    }
    if NOTIFICATION_LOG:
        data["alerts"] = list(NOTIFICATION_LOG)
    return data


__all__ = ["collect_analytics"]

