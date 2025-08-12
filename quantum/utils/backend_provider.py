"""Backend provider utilities with IBM Quantum integration and simulator fallback."""

from __future__ import annotations

import logging
import os
from typing import Optional

try:  # pragma: no cover - optional dependency
    import qiskit  # noqa: F401
except Exception as exc:  # pragma: no cover - qiskit may be missing
    raise ImportError(
        "qiskit is required; install qiskit==0.44.0"
    ) from exc

try:  # pragma: no cover - optional dependency
    from qiskit_aer import Aer
except Exception as exc:  # pragma: no cover - qiskit or Aer may be missing
    Aer = None
    _AER_IMPORT_ERROR = exc

try:  # pragma: no cover - optional dependency
    from qiskit_ibm_provider import IBMProvider
except Exception:  # pragma: no cover - provider may be missing
    IBMProvider = None

LOGGER = logging.getLogger(__name__)


def get_backend(
    name: str = "ibmq_qasm_simulator",
    use_hardware: bool | None = None,
    token: Optional[str] = None,
    token_env: str = "QISKIT_IBM_TOKEN",
):
    """Return a Qiskit backend with optional hardware selection.

    Attempts to load an IBM Quantum backend when ``use_hardware`` is True and the
    provider is available. Falls back to the Aer simulator otherwise. When
    ``use_hardware`` is ``None`` the ``QUANTUM_USE_HARDWARE`` environment variable
    ("1" enables hardware mode) controls the behavior.

    Parameters
    ----------
    name:
        Desired backend name when using hardware.
    use_hardware:
        If True, attempt to use an IBM Quantum backend. If ``None``, read the
        value from ``QUANTUM_USE_HARDWARE``.
    token:
        Optional IBM Quantum API token. If not provided the function falls back
        to the ``token_env`` environment variable.
    token_env:
        Name of the environment variable that may hold the token.

    Returns
    -------
    Any
        The selected backend instance.
    """

    if Aer is None:
        raise ImportError(
            "qiskit and qiskit-aer are required; install qiskit==0.44.0 and qiskit-aer==0.17.1"
        ) from _AER_IMPORT_ERROR

    if use_hardware is None:
        use_hardware = os.getenv("QUANTUM_USE_HARDWARE", "0") == "1"

    if use_hardware and IBMProvider is not None:
        try:  # pragma: no cover - requires network credentials
            tok = token or os.getenv(token_env)
            provider = IBMProvider(token=tok) if tok else IBMProvider()
            return provider.get_backend(name)
        except Exception as exc:  # pragma: no cover - provider may fail
            LOGGER.warning("IBM backend unavailable: %s; using simulator", exc)

    return Aer.get_backend("qasm_simulator")
