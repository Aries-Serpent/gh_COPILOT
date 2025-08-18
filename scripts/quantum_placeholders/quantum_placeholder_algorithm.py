"""Simulator parity verifier for quantum placeholders.

This module replaces the previous pass-through stub with a best-effort
parity check between two internal mock simulators. The implementation is
standalone and avoids external dependencies to maintain portability.
"""

from typing import Dict, Any

from . import ensure_not_production


def verify_simulator_parity(circuit: Dict[str, Any], shots: int = 1024) -> Dict[str, Any]:
    """Run a mock parity check between two lightweight simulators.

    Args:
        circuit: Simplified circuit description.
        shots: Number of samples for histogram-based simulator.

    Returns:
        Dictionary containing parity verdict and diagnostic details.
    """

    ensure_not_production()

    import json, hashlib, math

    def _stable_hash(s: str) -> int:
        return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

    class _MockStatevectorSim:
        name = "MockStatevectorSim"

        def run(self, circ: Dict[str, Any], shots: int = 1024) -> Dict[str, Any]:
            key = json.dumps(circ, sort_keys=True)
            h = hashlib.sha256(key.encode("utf-8")).digest()
            vals = [b / 255.0 for b in h[:4]]
            s = sum(vals) or 1.0
            vec = [v / s for v in vals]
            return {"type": "statevector", "vector": vec}

    class _MockSamplerSim:
        name = "MockSamplerSim"

        def run(self, circ: Dict[str, Any], shots: int = 1024) -> Dict[str, Any]:
            key = json.dumps(circ, sort_keys=True)
            seed = _stable_hash(key) % (2**32)
            probs_raw = [((seed >> k) & 0xFF) / 255.0 for k in (0, 8, 16, 24)]
            s = sum(probs_raw) or 1.0
            probs = [p / s for p in probs_raw]
            labels = ["00", "01", "10", "11"]
            counts = {lab: int(round(p * shots)) for lab, p in zip(labels, probs)}
            return {"type": "counts", "counts": counts, "shots": shots}

    def _hellinger(p: list[float], q: list[float]) -> float:
        return (1.0 / (2.0**0.5)) * (sum((math.sqrt(pi) - math.sqrt(qi)) ** 2 for pi, qi in zip(p, q))) ** 0.5

    def _norm_counts(counts: Dict[str, int]) -> list[float]:
        total = sum(counts.values()) or 1
        return [counts.get(k, 0) / total for k in ["00", "01", "10", "11"]]

    s1, s2 = _MockStatevectorSim(), _MockSamplerSim()
    r1, r2 = s1.run(circuit, shots), s2.run(circuit, shots)

    if r1["type"] == "statevector" and r2["type"] == "counts":
        v = r1["vector"]
        p = _norm_counts(r2["counts"])
        v_pad = (v + [0.0] * (4 - len(v)))[:4]
        d = _hellinger(v_pad, p)
        threshold = 0.35
        return {
            "parity": d <= threshold,
            "distance": d,
            "details": {"threshold": threshold, "metric": "hellinger"},
        }
    return {"parity": False, "details": {"reason": "incompatible types"}}
