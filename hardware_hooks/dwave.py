"""D-Wave hardware hook with token check and simulator fallback."""
from __future__ import annotations

import os
import warnings
from types import SimpleNamespace
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import dimod  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    dimod = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from dwave.system import DWaveSampler  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    DWaveSampler = None  # type: ignore


def load_token(env_var: str = "DWAVE_API_TOKEN") -> Optional[str]:
    """Return the API token from ``env_var`` if present."""
    token = os.getenv(env_var, "").strip()
    return token or None


def get_backend() -> Any:
    """Return a D-Wave sampler when available, otherwise a local simulator."""
    token = load_token()
    if DWaveSampler is not None and token:
        try:
            solver = os.getenv("DWAVE_SOLVER")
            return DWaveSampler(token=token, solver=solver)
        except Exception as exc:  # pragma: no cover - provider issues
            warnings.warn(f"D-Wave backend unavailable: {exc}; using simulator")
    if dimod is not None:
        try:
            return dimod.SimulatedAnnealingSampler()
        except Exception:  # pragma: no cover - sampler issues
            return SimpleNamespace(sample_qubo=lambda Q, **k: SimpleNamespace(first=None))
    return SimpleNamespace(sample_qubo=lambda Q, **k: SimpleNamespace(first=None))


def run_sample_circuit() -> Dict[str, Any]:
    """Solve a trivial QUBO using the selected sampler."""
    sampler = get_backend()
    Q = {("a", "a"): 1}
    try:
        response = sampler.sample_qubo(Q, num_reads=10)
        record = getattr(response, "first", None)
    except Exception as exc:  # pragma: no cover - runtime issues
        return {"status": "execution-failed", "error": str(exc)}
    return {
        "status": "ok",
        "backend": sampler.__class__.__name__,
        "record": record,
    }


__all__ = ["load_token", "get_backend", "run_sample_circuit"]
