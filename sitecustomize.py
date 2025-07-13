import sys


class _FallbackShor:
    def __init__(self, quantum_instance=None):
        self.quantum_instance = quantum_instance

    def factor(self, n):
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return type('Res', (), {'factors': [[i, n // i]]})()
        return type('Res', (), {'factors': [[n, 1]]})()


module = type(sys)('qiskit.algorithms')


module.Shor = _FallbackShor
sys.modules.setdefault('qiskit.algorithms', module)
