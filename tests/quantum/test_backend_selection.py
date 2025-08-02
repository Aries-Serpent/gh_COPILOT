from quantum.optimizers.quantum_optimizer import QuantumOptimizer


def test_backend_selection_hardware(monkeypatch):
    backend = object()
    monkeypatch.setattr(
        "quantum.optimizers.quantum_optimizer.init_ibm_backend",
        lambda **_: (backend, True),
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    opt.set_backend(None, use_hardware=True)
    assert opt.backend is backend
    assert opt.use_hardware


def test_backend_selection_simulator(monkeypatch):
    simulator = object()
    monkeypatch.setattr(
        "quantum.optimizers.quantum_optimizer.init_ibm_backend",
        lambda **_: (simulator, False),
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    opt.set_backend(None, use_hardware=True)
    assert opt.backend is simulator
    assert not opt.use_hardware
