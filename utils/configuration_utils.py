"""Configuration utilities for gh_COPILOT Enterprise Toolkit."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_enterprise_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load enterprise configuration from JSON or YAML with environment overrides."""
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))

    if config_path is None:
        config_path = workspace_root / "config" / "enterprise.json"
    else:
        config_path = Path(config_path)

    defaults = {
        "workspace_root": str(workspace_root),
        "database_path": "databases/production.db",
        "logging_level": "INFO",
        "enterprise_mode": True,
    }

    config: Dict[str, Any] = {}
    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            if config_path.suffix.lower() in {".yaml", ".yml"}:
                config = yaml.safe_load(fh) or {}
            else:
                config = json.load(fh)
    except FileNotFoundError:
        pass  # Use defaults only
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Invalid configuration file: {config_path}") from exc

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
    workspace = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
    return workspace.endswith("gh_COPILOT")


def operations___init__(workspace_path: Optional[str] = None,
                        config_path: Optional[str] = None) -> Dict[str, Any]:
    """Universal initialization pattern for scripts.

    This helper sets ``GH_COPILOT_WORKSPACE`` if ``workspace_path`` is provided
    and loads the enterprise configuration via :func:`load_enterprise_configuration`.
    """

    if workspace_path is not None:
        os.environ["GH_COPILOT_WORKSPACE"] = str(Path(workspace_path))

    config = load_enterprise_configuration(config_path)
    return config
