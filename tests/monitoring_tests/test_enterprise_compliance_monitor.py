from scripts.monitoring import enterprise_compliance_monitor as ecm


def test_functions_decorated():
    assert hasattr(ecm.setup_logger, "__wrapped__")
    assert hasattr(ecm.validate_logs, "__wrapped__")


def test_validator_called_each_cycle(tmp_path, monkeypatch):
    calls: list[list[str]] = []

    class DummyValidator:
        def validate_corrections(self, files):
            calls.append(list(files))
            return True

    monkeypatch.setattr(ecm, "SecondaryCopilotValidator", lambda: DummyValidator())

    logger = ecm.setup_logger(tmp_path)
    ecm.run_monitor(logger, cycles=2)

    log_file = tmp_path / "logs" / "enterprise_compliance_monitor.log"
    assert len(calls) == 2
    assert all(call == [str(log_file)] for call in calls)
