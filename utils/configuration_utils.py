"""Configuration utilities for gh_COPILOT Enterprise Toolkit."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from utils.cross_platform_paths import CrossPlatformPathManager

try:  # pragma: no cover - optional dependency
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required for configuration utilities. Install PyYAML to proceed."
    ) from exc


def load_enterprise_configuration(
    config_path: Path | str | None = None,
) -> Dict[str, Any]:
    """Load enterprise configuration from JSON or YAML with environment overrides."""
    workspace_root = CrossPlatformPathManager.get_workspace_path()

    cfg_path = (
        Path(config_path)
        if config_path is not None
        else workspace_root / "config" / "enterprise.json"
    )

    defaults = {
        "workspace_root": str(workspace_root),
        "database_path": "databases/production.db",
        "logging_level": "INFO",
        "enterprise_mode": True,
    }

    config: Dict[str, Any] = {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as fh:
            if cfg_path.suffix.lower() in {".yaml", ".yml"}:
                config = yaml.safe_load(fh) or {}
            else:
                config = json.load(fh)
    except FileNotFoundError:
        pass  # Use defaults only
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Invalid configuration file: {cfg_path}") from exc

    cfg = {**defaults, **config}

    for key in list(cfg.keys()):
        env_val = os.getenv(key.upper())
        if env_val is not None:
            cfg[key] = env_val

    required = ["workspace_root", "database_path", "logging_level", "enterprise_mode"]
    for field in required:
        if field not in cfg or cfg[field] in (None, ""):
            raise ValueError(f"Missing required configuration value: {field}")

    return cfg


def validate_environment_compliance() -> bool:
    """Validate enterprise environment compliance"""
    workspace = CrossPlatformPathManager.get_workspace_path()
    return str(workspace).endswith("gh_COPILOT")


def operations___init__(
    workspace_path: Path | str | None = None,
    config_path: Path | str | None = None,
) -> Dict[str, Any]:
    """Universal initialization pattern for scripts.

    This helper sets ``GH_COPILOT_WORKSPACE`` if ``workspace_path`` is provided
    and loads the enterprise configuration via :func:`load_enterprise_configuration`.
    """

    if workspace_path is not None:
        os.environ["GH_COPILOT_WORKSPACE"] = str(Path(workspace_path))

    config = load_enterprise_configuration(config_path)
    return config
