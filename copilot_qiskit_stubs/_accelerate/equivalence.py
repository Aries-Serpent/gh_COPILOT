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
    pass

class EquivalenceLibrary(BaseEquivalenceLibrary):
    pass

class Key:
    def __init__(self, name=None, num_qubits=0):
        self.name = name
        self.num_qubits = num_qubits

class Equivalence:
    def __init__(self, params, circuit):
        self.params = params
        self.circuit = circuit

class NodeData(dict):
    pass

class EdgeData(dict):
    pass
