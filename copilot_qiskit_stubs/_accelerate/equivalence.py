"""Fallback equivalence utilities for testing."""


class BaseEquivalenceLibrary:
    """Minimal placeholder class used during tests."""

    def __init__(self, base=None):
        self.base = base
        self.data = {}

    def add_equivalence(self, key, equiv):
        self.data.setdefault(key, []).append(equiv)

    def keys(self):
        return self.data.keys()


class SessionEquivalenceLibrary(BaseEquivalenceLibrary):
    """Session-scoped equivalence library used in tests."""

    def __init__(self, base=None, session_id=None):
        super().__init__(base)
        self.session_id = session_id


class EquivalenceLibrary(BaseEquivalenceLibrary):
    """Simple equivalence library placeholder."""

    def __init__(self, base=None):
        super().__init__(base)


class Key:
    def __init__(self, name=None, num_qubits=0):
        self.name = name
        self.num_qubits = num_qubits


class Equivalence:
    def __init__(self, params, circuit):
        self.params = params
        self.circuit = circuit


class NodeData(dict):
    """Dictionary wrapper for node attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EdgeData(dict):
    """Dictionary wrapper for edge attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
