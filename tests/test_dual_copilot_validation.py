import pytest

from utils.validation_utils import run_dual_copilot_validation


def test_primary_exception_still_runs_secondary():
    order = []

    def primary() -> bool:
        order.append("primary")
        raise ValueError("boom")

    def secondary() -> bool:
        order.append("secondary")
        return True

    with pytest.raises(RuntimeError) as excinfo:
        run_dual_copilot_validation(primary, secondary)

    assert "Primary validation error" in str(excinfo.value)
    assert order == ["primary", "secondary"]


def test_both_exceptions_are_reported():
    def primary() -> bool:
        raise ValueError("p")

    def secondary() -> bool:
        raise ValueError("s")

    with pytest.raises(RuntimeError) as excinfo:
        run_dual_copilot_validation(primary, secondary)

    message = str(excinfo.value)
    assert "Primary validation error" in message
    assert "Secondary validation error" in message
