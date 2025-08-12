"""Backend provider registry.

This module exposes a helper :func:`get_provider` that returns an instance of
the requested backend provider. Providers implement
``quantum.providers.base.BackendProvider``.
"""

from __future__ import annotations

from typing import Dict

from .base import BackendProvider
from .ibm import IBMBackendProvider
from .ionq import IonQProvider
from .rigetti import RigettiProvider
from .simulator import SimulatorProvider

# Mapping of provider names to their classes. Additional providers can be added
# here without modifying :func:`get_provider`.
_PROVIDERS: Dict[str, type[BackendProvider]] = {
    "simulator": SimulatorProvider,
    "ibm": IBMBackendProvider,
    "ionq": IonQProvider,
    "rigetti": RigettiProvider,
}


def get_provider(name: str) -> BackendProvider:
    """Return a provider instance by name.

    Unknown names default to the :class:`SimulatorProvider`.
    """

    provider_cls = _PROVIDERS.get(name, SimulatorProvider)
    return provider_cls()


__all__ = ["BackendProvider", "get_provider"]

