import json
from pathlib import Path


def test_deployment_config_loads() -> None:
    """Deployment configuration should be valid JSON."""
    path = Path("deployment/deployment_config.json")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)

