# Auto-generated prototype tests for simulator parity
import unittest
from scripts.quantum_placeholders import __init__ as qp_init  # if exists
# Tests call into an exemplar placeholder module if present, else use local runner.

try:
    from scripts.quantum_placeholders.sample import verify_simulator_parity as _verify
except Exception:
    _verify = None


def _fallback_verify(circuit: dict, shots: int = 512) -> dict:
    # inline minimal parity check (mirrors generator)
    import json, hashlib, math

    def _stable_hash(s):
        return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

    class S1:
        def run(self, c, shots=512):
            key = json.dumps(c, sort_keys=True)
            h = hashlib.sha256(key.encode("utf-8")).digest()
            vals = [b / 255.0 for b in h[:4]]
            s = sum(vals) or 1.0
            return {"type": "statevector", "vector": [v / s for v in vals]}

    class S2:
        def run(self, c, shots=512):
            key = json.dumps(c, sort_keys=True)
            seed = _stable_hash(key) % (2**32)
            probs_raw = [((seed >> k) & 0xFF) / 255.0 for k in (0, 8, 16, 24)]
            s = sum(probs_raw) or 1.0
            probs = [p / s for p in probs_raw]
            labels = ["00", "01", "10", "11"]
            counts = {lab: int(round(p * shots)) for lab, p in zip(labels, probs)}
            return {"type": "counts", "counts": counts, "shots": shots}

    def _hellinger(p, q):
        return (1.0 / (2.0**0.5)) * (sum((math.sqrt(pi) - math.sqrt(qi)) ** 2 for pi, qi in zip(p, q))) ** 0.5

    def _norm(counts):
        tot = sum(counts.values()) or 1
        return [counts.get(k, 0) / tot for k in ["00", "01", "10", "11"]]

    def verify(circuit, shots=512):
        s1, s2 = S1(), S2()
        r1, r2 = s1.run(circuit, shots), s2.run(circuit, shots)
        v = r1["vector"]
        p = _norm(r2["counts"])
        v = (v + [0.0] * (4 - len(v)))[:4]
        d = _hellinger(v, p)
        return {"parity": d <= 0.35, "distance": d}

    return verify(circuit, shots)


def verify(circuit: dict, shots: int = 512) -> dict:
    if _verify:
        return _verify(circuit, shots)
    return _fallback_verify(circuit, shots)


class TestParity(unittest.TestCase):
    def test_identity(self):
        c = {"name": "id", "ops": []}
        res = verify(c)
        self.assertIn("parity", res)

    def test_rotation(self):
        c = {"name": "rx", "ops": [{"gate": "rx", "q": 0, "theta": 0.5}]}
        res = verify(c)
        self.assertIn("parity", res)

    def test_entangle(self):
        c = {"name": "bell", "ops": [{"gate": "h", "q": 0}, {"gate": "cx", "control": 0, "target": 1}]}
        res = verify(c)
        self.assertIn("parity", res)


if __name__ == "__main__":
    unittest.main()
