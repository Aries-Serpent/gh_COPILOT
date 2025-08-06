"""Regression tests for compliance decorators."""

import pytest

from enterprise_modules.compliance import ComplianceError
from enterprise_modules.file_utils import write_file_safely
from utils.logging_utils import log_session_event


def test_write_file_safely_forbidden(monkeypatch, tmp_path):
    """write_file_safely raises when validation fails."""

    monkeypatch.setattr(
        "enterprise_modules.file_utils.validate_enterprise_operation",
        lambda *a, **k: False,
    )

    target = tmp_path / "bad.txt"
    target.touch()

    with pytest.raises(ComplianceError):
        write_file_safely(target, "data")


def test_log_session_event_forbidden(monkeypatch, tmp_path):
    """log_session_event raises when validation fails."""

    monkeypatch.setattr(
        "utils.logging_utils.validate_enterprise_operation",
        lambda *a, **k: False,
    )

    db_file = tmp_path / "db.sqlite"
    db_file.touch()

    with pytest.raises(ComplianceError):
        log_session_event("s", "e", db_path=db_file)



