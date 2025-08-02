import importlib
import sys
from pathlib import Path

MODULES = [
    "db_tools.script_database_validator",
    "scripts.automation.autonomous_database_health_optimizer",
    "dashboard.compliance_metrics_updater",
]


def test_modules_importable():
    """Ensure core modules resolve without sys.path hacking."""
    root = Path(__file__).resolve().parents[1]
    assert str(root) in sys.path
    for name in MODULES:
        module = importlib.import_module(name)
        assert module is not None
