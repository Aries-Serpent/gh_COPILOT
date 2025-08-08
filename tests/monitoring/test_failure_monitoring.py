from src.monitoring import alerts


def test_monitor_failures_triggers_routines():
    messages = ["service alpha down", "state cache corrupt"]
    calls = {"service_crash": 0, "state_corruption": 0}

    def restart() -> None:
        calls["service_crash"] += 1

    def revert() -> None:
        calls["state_corruption"] += 1

    results = alerts.monitor_failures(
        messages,
        {"service_crash": restart, "state_corruption": revert},
    )
    assert results == {"service_crash": True, "state_corruption": True}
    assert calls == {"service_crash": 1, "state_corruption": 1}
