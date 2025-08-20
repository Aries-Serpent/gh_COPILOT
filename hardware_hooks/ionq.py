"""IonQ hardware hook with token check and simulator fallback."""
from __future__ import annotations

import os
import warnings
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    from qiskit import Aer, QuantumCircuit  # type: ignore
    from qiskit_ionq import IonQProvider  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Aer = None  # type: ignore
    QuantumCircuit = None  # type: ignore
    IonQProvider = None  # type: ignore


def load_token(env_var: str = "IONQ_API_KEY") -> Optional[str]:
    """Return the API key from ``env_var`` if present."""
    token = os.getenv(env_var, "").strip()
    return token or None


def get_backend() -> Any:
    """Return an IonQ backend when available, otherwise a simulator."""
    token = load_token()
    if IonQProvider is not None and token:
        try:
            provider = IonQProvider(api_key=token)
            backend_name = os.getenv("IONQ_BACKEND")
            if backend_name:
                return provider.get_backend(backend_name)
            hardware = provider.backends(simulator=False)
            return hardware[0] if hardware else provider.get_backend("ionq.simulator")
        except Exception as exc:  # pragma: no cover - provider issues
            warnings.warn(f"IonQ backend unavailable: {exc}; using simulator")
    if Aer is not None:
        return Aer.get_backend("aer_simulator")
    return None


def _finalize(result: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the result dictionary exposes the expected keys."""

    result.setdefault("status", "unknown")
    result.setdefault("backend", None)
    result.setdefault("counts", None)
    return result


def run_sample_circuit() -> Dict[str, Any]:
    """Execute a small circuit on the selected backend.

    The returned dictionary always contains ``status``, ``backend`` and
    ``counts`` keys with fallback values when a backend or provider is
    unavailable.
    """
    if QuantumCircuit is None:
        return _finalize({"status": "qiskit-unavailable"})
    backend = get_backend()
    if backend is None:
        return _finalize({"status": "backend-unavailable"})
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    try:
        job = backend.run(qc)
        result = job.result() if hasattr(job, "result") else job
        counts = result.get_counts() if hasattr(result, "get_counts") else None
    except Exception as exc:  # pragma: no cover - runtime issues
        return _finalize(
            {
                "status": "execution-failed",
                "backend": getattr(backend, "name", lambda: str(backend))()
                if backend
                else None,
                "error": str(exc),
            }
        )
    return _finalize(
        {
            "status": "ok",
            "backend": getattr(backend, "name", lambda: str(backend))(),
            "counts": counts,
        }
    )


__all__ = ["load_token", "get_backend", "run_sample_circuit"]
