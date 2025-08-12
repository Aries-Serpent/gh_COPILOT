"""Helper for retrieving quantum backend providers."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .base import BackendProvider

_PROVIDERS: Dict[str, str] = {
    "simulator": "quantum.providers.simulator.SimulatorProvider",
    "ibm": "quantum.providers.ibm_provider.IBMBackendProvider",
    "ionq": "quantum.providers.ionq_provider.IonQProvider",
    "rigetti": "quantum.providers.rigetti_provider.RigettiProvider",
    "dwave": "quantum.providers.dwave_provider.DWaveProvider",
}


def _load_provider(path: str) -> "BackendProvider":
    module_name, class_name = path.rsplit(".", 1)
    module = import_module(module_name)
    provider_cls: Type["BackendProvider"] = getattr(module, class_name)
    return provider_cls()


def get_provider(name: str) -> "BackendProvider":
    """Return a provider instance by name.

    Unknown names default to the simulator provider.
    """

    path = _PROVIDERS.get(name, _PROVIDERS["simulator"])
    return _load_provider(path)


__all__ = ["get_provider"]
