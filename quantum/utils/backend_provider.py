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


def get_backend(name: str = "ibmq_qasm_simulator", use_hardware: bool | None = None):
    """Return a Qiskit backend with optional hardware selection.

    Attempts to load an IBM Quantum backend when ``use_hardware`` is True and the
    provider is available. Falls back to the Aer simulator otherwise. When
    ``use_hardware`` is ``None`` the ``QUANTUM_USE_HARDWARE`` environment variable
    ("1" enables hardware mode) controls the behavior.

    Args:
        name: Desired backend name when using hardware.
        use_hardware: If True, attempt to use an IBM Quantum backend. If ``None``,
            read the value from ``QUANTUM_USE_HARDWARE``.

    Returns:
        The selected backend instance or ``None`` if Qiskit is unavailable.
    """
    if Aer is None:
        LOGGER.warning("Qiskit Aer not available; no backend returned")
        return None

    if use_hardware is None:
        use_hardware = os.getenv("QUANTUM_USE_HARDWARE", "0") == "1"

    if use_hardware and IBMProvider is not None:
        try:  # pragma: no cover - requires network credentials
            provider = IBMProvider()
            return provider.get_backend(name)
        except Exception as exc:  # pragma: no cover - provider may fail
            LOGGER.warning("IBM backend unavailable: %s; using simulator", exc)

    return Aer.get_backend("qasm_simulator")
