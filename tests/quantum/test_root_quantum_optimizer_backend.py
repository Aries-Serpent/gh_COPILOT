import logging
import numpy as np
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


def test_example_usage_logs(caplog):
    def quad_obj(x):
        return float(np.sum((x - 2.0) ** 2))

    bounds = [(-5, 5), (-5, 5)]
    opt = qo.QuantumOptimizer(
        objective_function=quad_obj, variable_bounds=bounds, method="simulated_annealing"
    )
    with caplog.at_level(logging.INFO):
        summary = opt.run(max_iter=1)
        qo.logger.info("Optimization result:")
        qo.logger.info(summary["result"])
        qo.logger.info("History:")
        for event in summary["history"]:
            qo.logger.info(event)

    messages = [rec.getMessage() for rec in caplog.records]
    assert "Optimization result:" in messages
    assert "History:" in messages
