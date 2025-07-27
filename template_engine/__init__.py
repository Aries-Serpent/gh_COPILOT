"""Top-level interface for :mod:`template_engine`.

This package lazily exposes submodules used throughout the project. Public
APIs include :mod:`auto_generator`, :mod:`db_first_code_generator`,
:mod:`pattern_mining_engine`, and :mod:`template_synchronizer`. Accessing an
attribute imports the underlying module on first use. The helper
:func:`_log_event` is re-exported from :mod:`log_utils` for convenience.

All unrecoverable states raise :class:`RuntimeError`. Malformed template data
raise :class:`ValueError`.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from . import auto_generator  # noqa: F401
    from . import db_first_code_generator  # noqa: F401
    from . import log_utils  # noqa: F401
    from . import objective_similarity_scorer  # noqa: F401
    from . import pattern_clustering_sync  # noqa: F401
    from . import pattern_mining_engine  # noqa: F401
    from . import placeholder_utils  # noqa: F401
    from . import template_placeholder_remover  # noqa: F401
    from . import template_synchronizer  # noqa: F401
    from . import workflow_enhancer  # noqa: F401

__all__ = [
    "auto_generator",
    "db_first_code_generator",
    "log_utils",
    "objective_similarity_scorer",
    "pattern_clustering_sync",
    "pattern_mining_engine",
    "placeholder_utils",
    "template_placeholder_remover",
    "template_synchronizer",
    "workflow_enhancer",
    "pattern_templates",
]


def __getattr__(name: str):
    if name in __all__:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    if name == "_log_event":
        module = import_module(f"{__name__}.log_utils")
        value = getattr(module, "_log_event")
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
