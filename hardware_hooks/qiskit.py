"""Qiskit hardware hook with token check and simulator fallback."""
from __future__ import annotations

import os
import warnings
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    from qiskit import Aer, QuantumCircuit  # type: ignore
    from qiskit_ibm_provider import IBMProvider  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Aer = None  # type: ignore
    QuantumCircuit = None  # type: ignore
    IBMProvider = None  # type: ignore


def load_token(env_var: str = "QISKIT_IBM_TOKEN") -> Optional[str]:
    """Return the API token from ``env_var`` if present."""
    token = os.getenv(env_var, "").strip()
    return token or None


def get_backend() -> Any:
    """Return an IBM backend when available, otherwise a simulator."""
    token = load_token()
    if IBMProvider is not None and token:
        try:
            provider = IBMProvider(token=token)
            backend_name = os.getenv("IBM_BACKEND")
            if backend_name:
                return provider.get_backend(backend_name)
            hardware = provider.backends(simulator=False, operational=True)
            return hardware[0] if hardware else provider.get_backend("aer_simulator")
        except Exception as exc:  # pragma: no cover - provider issues
            warnings.warn(f"IBM backend unavailable: {exc}; using simulator")
    if Aer is not None:
        return Aer.get_backend("aer_simulator")
    return None


def _finalize(result: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure expected keys exist in the result dictionary.

    The hooks are consumed in contexts that assume the presence of
    ``status``, ``backend`` and ``counts`` keys. When optional
    dependencies are missing, the original implementation returned
    dictionaries without some of these keys, leading to ``KeyError``
    on access. This helper backfills any missing keys with ``None`` or
    sensible defaults to provide a stable contract.
    """

    result.setdefault("status", "unknown")
    result.setdefault("backend", None)
    result.setdefault("counts", None)
    return result


def run_sample_circuit() -> Dict[str, Any]:
    """Execute a small circuit on the selected backend.

    The returned dictionary always contains ``status``, ``backend`` and
    ``counts`` keys. When neither the provider nor the simulator is
    available, those keys are populated with fallback values instead of
    being omitted.
    """
    if QuantumCircuit is None:
        return _finalize({"status": "qiskit-unavailable"})
    backend = get_backend()
    if backend is None:
        return _finalize({"status": "backend-unavailable"})
    qc = QuantumCircuit(1, 1)
    qc.h(0)
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
