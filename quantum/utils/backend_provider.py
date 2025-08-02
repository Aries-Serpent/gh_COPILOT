"""Backend provider utilities with IBM Quantum integration and simulator fallback."""

from __future__ import annotations

import logging
import os

try:  # pragma: no cover - optional dependency
    from qiskit import Aer
except Exception:  # pragma: no cover - qiskit may be missing
    try:  # fallback to BasicAer if available
        from qiskit.providers.basicaer import QasmSimulator

        class _AerShim:  # pragma: no cover - simple shim
            @staticmethod
            def get_backend(name: str):
                if name == "qasm_simulator":
                    return QasmSimulator()
                raise ValueError("Backend not available")

        Aer = _AerShim()
    except Exception:
        Aer = None

try:  # pragma: no cover - optional dependency
    from qiskit_ibm_provider import IBMProvider
except Exception:  # pragma: no cover - provider may be missing
    IBMProvider = None

LOGGER = logging.getLogger(__name__)


def _load_provider():
    """Return an :class:`IBMProvider` instance if available and configured."""

    if IBMProvider is None:
        return None

    token = os.getenv("QISKIT_IBM_TOKEN")
    try:  # pragma: no cover - network dependent
        if token:
            return IBMProvider(token=token)
        return IBMProvider()
    except Exception as exc:  # pragma: no cover - provider may fail
        LOGGER.debug("IBMProvider unavailable: %s", exc)
        return None


def get_backend(name: str = "ibmq_qasm_simulator", use_hardware: bool | None = None):
    """Return a Qiskit backend with optional hardware selection.

    When ``use_hardware`` is ``None`` the function automatically enables hardware
    mode if the ``qiskit-ibm-provider`` package is installed and a token is
    available via ``QISKIT_IBM_TOKEN``. ``QUANTUM_USE_HARDWARE`` ("1" or "0")
    overrides this auto-detection. Falls back to the local ``Aer`` simulator when
    a hardware backend cannot be selected.

    Args:
        name: Desired backend name when using hardware.
        use_hardware: If True, force hardware usage; if False force simulator;
            if ``None`` auto-detect based on environment variables.

    Returns:
        The selected backend instance or ``None`` if Qiskit is unavailable.
    """
    if Aer is None:
        LOGGER.warning("Qiskit Aer not available; no backend returned")
        return None

    provider = None

    if use_hardware is None:
        env = os.getenv("QUANTUM_USE_HARDWARE")
        if env is not None:
            use_hardware = env == "1"
        else:
            provider = _load_provider()
            use_hardware = provider is not None

    if use_hardware:
        provider = provider or _load_provider()
        if provider is not None:
            try:  # pragma: no cover - requires network credentials
                return provider.get_backend(name)
            except Exception as exc:  # pragma: no cover - provider may fail
                LOGGER.warning("IBM backend unavailable: %s; using simulator", exc)

    return Aer.get_backend("qasm_simulator")
