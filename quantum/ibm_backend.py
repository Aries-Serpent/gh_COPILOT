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
    backend_name: str | None = None,
    token_env: str = "QISKIT_IBM_TOKEN",
    backend_env: str = "IBM_BACKEND",
    enforce_hardware: bool = False,
) -> Tuple[Any, bool]:
    """Initialize an IBM quantum backend.

    Returns a tuple ``(backend, use_hardware)``. If hardware initialization
    fails or dependencies are missing, a simulator backend is returned with
    ``use_hardware`` set to ``False`` unless ``enforce_hardware`` is ``True``.
    When ``enforce_hardware`` is enabled and hardware cannot be initialized, a
    ``RuntimeError`` is raised. Optional ``token`` and ``backend_name``
    parameters override environment variables for configuration.
    """
    token = token or os.getenv(token_env) or _load_token_from_config()
    backend_name = backend_name or os.getenv(backend_env)

    if IBMProvider is None or Aer is None:
        msg = "qiskit or qiskit-ibm-provider not installed"
        if enforce_hardware:
            raise RuntimeError(f"{msg}; cannot access hardware backend")
        warnings.warn(f"{msg}; using simulator")
        if Aer is None:
            return None, False
        return Aer.get_backend("aer_simulator"), False

    if not token:
        if enforce_hardware:
            raise RuntimeError(
                f"IBM Quantum token not found in env '{token_env}' and no token provided"
            )
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
            # ``provider.backends`` may return a MagicMock in tests. If so,
            # defer to ``provider.get_backend`` to retrieve a concrete backend.
            if isinstance(hardware, list):
                return hardware[0], True
            return provider.get_backend(None), True
        warnings.warn("No operational hardware backend found; using simulator")
    except Exception as exc:  # pragma: no cover - provider issues
        if enforce_hardware:
            raise RuntimeError(
                f"Hardware backend '{backend_name or 'auto'}' unavailable: {exc}"
            ) from exc
        warnings.warn(
            f"Hardware backend '{backend_name or 'auto'}' unavailable: {exc}; using simulator",
        )
    return Aer.get_backend("aer_simulator"), False
