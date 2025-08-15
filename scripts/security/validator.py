#!/usr/bin/env python3
"""Load security configuration files.

This utility aggregates JSON configuration files stored under the
repository's :mod:`security` directory. It is intended for quick
validation or inspection of available security settings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "security"

def load_security_configs() -> Dict[str, Any]:
    """Return parsed security configuration data.

    Every ``*.json`` file inside :data:`CONFIG_DIR` is loaded and the
    resulting mapping of filenames to parsed JSON objects is returned.
    """
    configs: Dict[str, Any] = {}
    for path in CONFIG_DIR.glob("*.json"):
        with path.open(encoding="utf-8") as handle:
            configs[path.name] = json.load(handle)
    return configs

def main() -> None:
    configs = load_security_configs()
    names = ", ".join(sorted(configs))
    print(f"Loaded {len(configs)} config file(s): {names}")

if __name__ == "__main__":
    main()
