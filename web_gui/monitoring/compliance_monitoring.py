"""Compliance monitoring helpers for the web GUI."""

from __future__ import annotations

from typing import Dict, List

__all__ = [
    "ComplianceMetricsCollector",
    "DictExporter",
    "collect_compliance_metrics",
    "check_compliance",
]


REQUIRED_KEYS = {"policy", "status"}


class ComplianceMetricsCollector:
    """Collect basic compliance information from provided data."""

    def collect(self, data: Dict[str, str]) -> Dict[str, object]:
        missing: List[str] = sorted(REQUIRED_KEYS - data.keys())
        return {"is_compliant": not missing, "missing": missing}


class DictExporter:
    """Return compliance metrics as a dictionary."""

    def export(self, metrics: Dict[str, object]) -> Dict[str, object]:
        return metrics


def collect_compliance_metrics(data: Dict[str, str]) -> Dict[str, object]:
    """Collect and export compliance information for *data*."""
    collector = ComplianceMetricsCollector()
    exporter = DictExporter()
    return exporter.export(collector.collect(data))


def check_compliance(data: Dict[str, str]) -> bool:
    """Return ``True`` if required compliance keys are present."""
    return collect_compliance_metrics(data)["is_compliant"]
