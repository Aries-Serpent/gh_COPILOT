"""Configuration utilities for gh_COPILOT Enterprise Toolkit."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def _load_config_file(path: Path) -> Dict[str, Any]:
    """Return parsed configuration from ``path`` supporting JSON or YAML."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise

    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def load_enterprise_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load enterprise configuration with defaults and environment overrides."""
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))

    if config_path is None:
        config_path = workspace_root / "config" / "enterprise.json"
    else:
        config_path = Path(config_path)

    defaults: Dict[str, Any] = {
        "workspace_root": str(workspace_root),
        "database_path": "databases/production.db",
        "logging_level": "INFO",
        "enterprise_mode": True,
    }

    try:
        loaded = _load_config_file(config_path)
    except FileNotFoundError:
        loaded = {}
    except Exception:  # pragma: no cover - log and continue
        loaded = {}
    defaults.update(loaded)

    # Environment overrides
    if os.getenv("GH_COPILOT_DATABASE"):
        defaults["database_path"] = os.getenv("GH_COPILOT_DATABASE")
    if os.getenv("GH_COPILOT_LOG_LEVEL"):
        defaults["logging_level"] = os.getenv("GH_COPILOT_LOG_LEVEL")

    return defaults


def validate_environment_compliance() -> bool:
    """Validate enterprise environment compliance"""
    workspace = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
    return workspace.endswith("gh_COPILOT")
