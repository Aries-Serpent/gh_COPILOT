def sample_latency(fn):
    def _w(*a, **k): return fn(*a, **k)
    return _w
