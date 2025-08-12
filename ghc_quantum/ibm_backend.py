import json
import os
import warnings
from pathlib import Path
from typing import Any, Tuple

try:  # pragma: no cover - optional dependency
    from qiskit import Aer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Aer = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from qiskit_ibm_provider import IBMProvider  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    IBMProvider = None  # type: ignore

CONFIG_PATH = Path("config/qiskit.json")


def _load_token_from_config() -> str | None:
    if not CONFIG_PATH.exists():
        return None
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except Exception:  # pragma: no cover - config issues
        return None
    return data.get("QISKIT_IBM_TOKEN")


def init_ibm_backend(
    token: str | None = None,
    token_env: str = "QISKIT_IBM_TOKEN",
    backend_env: str = "IBM_BACKEND",
    backend_name: str | None = None,
) -> Tuple[Any, bool]:
    """Initialize an IBM quantum backend.

    Parameters
    ----------
    token:
        Optional API token. When provided it takes precedence over
        environment variables and configuration files.
    token_env:
        Name of the environment variable that may contain the token.
    backend_env:
        Environment variable for selecting a specific backend.
    backend_name:
        Optional explicit backend name. Overrides ``backend_env`` when provided.

    Returns
    -------
    tuple
        ``(backend, use_hardware)`` where ``backend`` is either a hardware
        backend or the local simulator and ``use_hardware`` indicates whether
        hardware execution will be used.
    """
    token = token or os.getenv(token_env) or _load_token_from_config()
    backend_name = backend_name or os.getenv(backend_env)

    if IBMProvider is None or Aer is None:
        warnings.warn(
            "qiskit or qiskit-ibm-provider not installed; using simulator",
        )
        if Aer is None:
            return None, False
        return Aer.get_backend("aer_simulator"), False

    if not token:
        warnings.warn(
            f"IBM Quantum token not found in env '{token_env}'; using simulator",
        )
        return Aer.get_backend("aer_simulator"), False

    try:
        provider = IBMProvider(token=token)
        if backend_name:
            backend = provider.get_backend(backend_name)
            return backend, True

        hardware = provider.backends(simulator=False, operational=True)
        if hardware:
            return hardware[0], True
        warnings.warn("No operational hardware backend found; using simulator")
    except Exception as exc:  # pragma: no cover - provider issues
        warnings.warn(
            f"Hardware backend '{backend_name or 'auto'}' unavailable: {exc}; using simulator",
        )
    return Aer.get_backend("aer_simulator"), False
