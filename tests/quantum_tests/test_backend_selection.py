from ghc_quantum.optimizers.quantum_optimizer import QuantumOptimizer


class _DummyHardwareBackend:
    name = "dummy_hardware"

    class _Cfg:
        simulator = False

    def configuration(self):
        return self._Cfg()


class _DummySimulatorBackend:
    name = "dummy_simulator"

    class _Cfg:
        simulator = True

    def configuration(self):
        return self._Cfg()


def test_backend_selection_hardware(monkeypatch):
    backend = _DummyHardwareBackend()
    monkeypatch.setattr(
        "ghc_quantum.optimizers.quantum_optimizer.get_backend",
        lambda name, use_hardware: backend,
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    opt.set_backend(None, use_hardware=True)
    assert opt.backend is backend
    assert opt.use_hardware


def test_backend_selection_simulator(monkeypatch):
    simulator = _DummySimulatorBackend()
    monkeypatch.setattr(
        "ghc_quantum.optimizers.quantum_optimizer.get_backend",
        lambda name, use_hardware: simulator,
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    opt.set_backend(None, use_hardware=True)
    assert opt.backend is simulator
    assert not opt.use_hardware
