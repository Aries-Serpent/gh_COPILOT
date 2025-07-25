"""High-level template engine utilities.

The package exposes several lazily imported modules:

* ``auto_generator`` – database-first template generation utilities.
* ``template_synchronizer`` – synchronization helpers with rollback.
* ``log_utils._log_event`` – structured analytics logging helper.

Unknown attribute access raises ``AttributeError``.
"""
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from utils import log_utils

    from . import auto_generator, template_synchronizer

__all__ = ["auto_generator", "template_synchronizer", "log_utils", "_log_event"]


def __getattr__(name: str):
    if name in ("auto_generator", "template_synchronizer"):
        return import_module(f".{name}", __name__)
    if name == "log_utils":
        return import_module("utils.log_utils")
    if name == "_log_event":
        module = import_module("utils.log_utils")
        return getattr(module, "_log_event")
    raise AttributeError(f"module {__name__} has no attribute {name}")
