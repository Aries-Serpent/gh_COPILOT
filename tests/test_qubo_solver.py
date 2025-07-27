#!/usr/bin/env python3
import logging

from scripts.optimization.advanced_qubo_optimization import solve_qubo_bruteforce


class DummyTqdm:
    """Minimal tqdm replacement for progress validation."""

    def __init__(self, iterable, *args, **kwargs):
        self.iterable = list(iterable)
        self.updates = 0

    def __iter__(self):
        for item in self.iterable:
            self.updates += 1
            yield item

    def set_postfix(self, data):
        pass

    def close(self):
        pass

logging.getLogger().setLevel(logging.CRITICAL)


def test_solve_qubo_bruteforce(monkeypatch):
    matrix = [[1.0, -2.0], [-2.0, 1.0]]
    bars = []

    def dummy_tqdm(iterable, *args, **kwargs):
        bar = DummyTqdm(iterable)
        bars.append(bar)
        return bar

    monkeypatch.setattr(
        "scripts.optimization.advanced_qubo_optimization.tqdm", dummy_tqdm
    )

    solution, energy = solve_qubo_bruteforce(matrix)

    assert solution == [1, 1]
    assert energy == -2.0
    assert bars and bars[0].updates == 4
