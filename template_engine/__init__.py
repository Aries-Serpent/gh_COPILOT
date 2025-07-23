"""Template engine package with lazy imports."""
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from . import auto_generator, template_synchronizer

__all__ = ["auto_generator", "template_synchronizer"]


def __getattr__(name: str):
    if name in __all__:
        return import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__} has no attribute {name}")
