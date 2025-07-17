"""Configuration utilities for gh_COPILOT Enterprise Toolkit"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

def load_enterprise_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load enterprise configuration with defaults"""
    if config_path is None:
        config_path = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT") + "/config/enterprise.json"
    
    defaults = {
        "workspace_root": os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"),
        "database_path": "databases/production.db",
        "logging_level": "INFO",
        "enterprise_mode": True
    }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        defaults.update(config)
    except FileNotFoundError:
        pass  # Use defaults
    
    return defaults

def validate_environment_compliance() -> bool:
    """Validate enterprise environment compliance"""
    workspace = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")
    return workspace.endswith("gh_COPILOT")
