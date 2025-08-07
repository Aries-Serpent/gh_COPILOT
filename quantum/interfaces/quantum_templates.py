"""Template management for quantum operations."""

from typing import Dict

_TEMPLATES: Dict[str, str] = {
    "bell_pair": "placeholder bell pair circuit",
    "noop": "no-op circuit",
}


def get_template(name: str) -> str:
    """Retrieve a quantum template by name."""

    return _TEMPLATES.get(name, "template not found")
