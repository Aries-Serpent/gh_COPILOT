"""Core template engine package with lazy imports.

The package exposes several submodules used throughout the project. Public APIs
include :mod:`auto_generator`, :mod:`db_first_code_generator`,
:mod:`pattern_mining_engine` and :mod:`template_synchronizer`. Importing a
submodule will automatically load it on first access.

Error handling is performed via ``RuntimeError`` for unrecoverable states (like
recursive folder detection) and ``ValueError`` for malformed templates. Logging
is routed through :mod:`utils.log_utils`.
"""
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["template_synchronizer"]
