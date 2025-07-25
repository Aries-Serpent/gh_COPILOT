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

# The package exposes several submodules used throughout the project. Public APIs
# include :mod:`auto_generator`, :mod:`db_first_code_generator`,
# :mod:`pattern_mining_engine` and :mod:`template_synchronizer`. Importing a
# submodule will automatically load it on first access.
#
# Error handling is performed via ``RuntimeError`` for unrecoverable states (like
# recursive folder detection) and ``ValueError`` for malformed templates. Logging
# is routed through :mod:`utils.log_utils`.

__all__ = ["template_synchronizer"]
