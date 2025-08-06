import logging

from validation.protocols.code_generation import run_dual_validation


def test_run_dual_validation_logs_conflict(caplog):
    """Both copilots execute and discrepancies are logged."""

    caplog.set_level(logging.INFO)

    def primary():
        logging.info("primary executed")
        return "alpha"

    def secondary():
        logging.info("secondary executed")
        return "beta"

    run_dual_validation(primary, secondary)

    logs = caplog.text
    assert "primary executed" in logs
    assert "secondary executed" in logs
    assert "discrepancy" in logs.lower()

