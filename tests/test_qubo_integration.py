#!/usr/bin/env python3
import logging

from scripts.automation.quantum_integration_orchestrator import integrate_qubo_problems


class DummyTqdm:
    """Minimal iterable tqdm replacement for testing."""

    def __init__(self, iterable, *args, **kwargs):
        self.iterable = list(iterable)
        self.updates = 0

    def __iter__(self):
        for item in self.iterable:
            self.updates += 1
            yield item

logging.getLogger().setLevel(logging.CRITICAL)


def test_integrate_qubo_problems():
    qubos = [
        [[1.0, -2.0], [-2.0, 1.0]],
        [[2.0, -1.0], [-1.0, 2.0]],
    ]
    solution, energy = integrate_qubo_problems(qubos)
    assert solution == [1, 1]
    assert energy == -2.0


def test_progress_bar(monkeypatch):
    qubos = [
        [[1.0, -2.0], [-2.0, 1.0]],
        [[2.0, -1.0], [-1.0, 2.0]],
    ]

    bars = []

    def dummy_tqdm(iterable, *args, **kwargs):
        bar = DummyTqdm(iterable, *args, **kwargs)
        bars.append(bar)
        return bar

    monkeypatch.setattr(
        "scripts.automation.quantum_integration_orchestrator.tqdm", dummy_tqdm
    )
    integrate_qubo_problems(qubos)
    assert bars and bars[0].updates == len(qubos)
