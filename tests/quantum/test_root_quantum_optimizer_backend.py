import quantum_optimizer as qo


class _DummyHardwareBackend:
    name = "dummy_hardware"

    class _Cfg:
        simulator = False

    def configuration(self):
        return self._Cfg()


def test_configure_backend_hardware(monkeypatch):
    monkeypatch.setattr(
        qo, "get_backend", lambda name, use_hardware: _DummyHardwareBackend()
    )
    opt = qo.QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    backend = opt.configure_backend(use_hardware=True)
    assert backend.name == "dummy_hardware"
    assert opt.use_hardware


def test_run_fallback_to_simulator(monkeypatch):
    monkeypatch.setattr(qo, "get_backend", lambda name, use_hardware: None)
    opt = qo.QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    summary = opt.run()
    assert "result" in summary
    assert not opt.use_hardware
