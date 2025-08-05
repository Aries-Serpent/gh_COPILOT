import pytest


def test_database_migration_verifier_runs_validator(monkeypatch):
    from scripts.database import database_migration_verifier as dmv

    monkeypatch.setattr(dmv.DatabaseMigrationVerifier, "execute_verification", lambda self: None)

    called = {}

    def fake_validation(primary, secondary):
        called["called"] = True
        return primary() and secondary()

    monkeypatch.setattr(dmv, "run_dual_copilot_validation", fake_validation)

    dmv.main()
    assert called["called"] is True


def test_database_migration_verifier_validator_failure(monkeypatch):
    from scripts.database import database_migration_verifier as dmv

    monkeypatch.setattr(dmv.DatabaseMigrationVerifier, "execute_verification", lambda self: None)

    def fake_validation(primary, secondary):
        raise RuntimeError("validation failed")

    monkeypatch.setattr(dmv, "run_dual_copilot_validation", fake_validation)

    with pytest.raises(RuntimeError, match="validation failed"):
        dmv.main()
