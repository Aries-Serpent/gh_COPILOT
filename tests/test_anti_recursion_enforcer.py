import logging
import psutil
from scripts.session.anti_recursion_enforcer import AntiRecursionEnforcer


def test_enforcer_skips_missing_pid(caplog):
    enforcer = AntiRecursionEnforcer()
    missing_pid = max(psutil.pids()) + 10000
    with caplog.at_level(logging.WARNING):
        enforcer.enforce_no_recursion(missing_pid)
    assert f"PID {missing_pid} not found" in caplog.text
