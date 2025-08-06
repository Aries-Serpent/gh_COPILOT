"""Tests ensuring migration validators are invoked."""

from __future__ import annotations

from pathlib import Path

import scripts.database.add_violation_logs as av
import scripts.database.add_rollback_logs as ar


def _setup_mocks(module, monkeypatch, calls):
    def fake_validate(path: str) -> bool:
        calls["validate"] = path
        return True

    class DummyValidator:
        def validate_corrections(self, targets):  # pragma: no cover - simple collector
            calls["dual"] = list(targets)

    class DummyOrchestrator:
        def __init__(self, *_, **__):
            self.validator = DummyValidator()

    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation", fake_validate
    )
    monkeypatch.setattr(
        "scripts.validation.dual_copilot_orchestrator.DualCopilotOrchestrator",
        DummyOrchestrator,
    )


def test_violation_logs_validators(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}
    _setup_mocks(av, monkeypatch, calls)
    db = tmp_path / "analytics.db"
    av.add_table(db)
    assert calls["validate"] == str(db)
    assert calls["dual"] == [str(db)]


def test_rollback_logs_validators(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}
    _setup_mocks(ar, monkeypatch, calls)
    db = tmp_path / "analytics.db"
    ar.add_table(db)
    assert calls["validate"] == str(db)
    assert calls["dual"] == [str(db)]

