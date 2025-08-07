"""Template management for quantum operations.

The real project stores templates in a database but for testing we keep a
very small in-memory registry.  Templates are simple callables that accept a
single argument and return a processed value.  Additional templates can be
registered at runtime using :func:`register_template`.
"""

from typing import Any, Callable, Dict

_TEMPLATES: Dict[str, Callable[[Any], Any]] = {
    "identity": lambda x: x,
    "increment": lambda x: x + 1 if x is not None else 1,
    "double": lambda x: (x or 0) * 2,
}


def register_template(name: str, template: Callable[[Any], Any]) -> None:
    """Register ``template`` under ``name``.

    Overwrites any existing template with the same name.
    """

    _TEMPLATES[name] = template


def get_template(name: str) -> Callable[[Any], Any]:
    """Retrieve a quantum template by ``name``.

    Raises
    ------
    KeyError
        If no template with ``name`` exists.
    """

    if name not in _TEMPLATES:
        raise KeyError(f"Unknown template: {name}")
    return _TEMPLATES[name]


__all__ = ["get_template", "register_template"]
