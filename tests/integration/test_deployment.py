"""Integration tests for deployment configuration."""

import json
from pathlib import Path


def test_deployment_config_has_name() -> None:
    """The deployment configuration should define a name."""
    config_path = Path("deployment/deployment_config.json")
    data = json.loads(config_path.read_text())
    assert "deployment_name" in data

