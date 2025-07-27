from pathlib import Path

import pytest

from scripts.optimization import optimize_to_100_percent, security_compliance_enhancer
from utils import database_utils


class DummyCursor:
    def execute(self, *a, **kw):
        pass

    def executemany(self, *a, **kw):
        pass

    def fetchone(self):
        return None

    def fetchall(self):
        return []


class DummyConn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def cursor(self):
        return DummyCursor()

    def commit(self):
        pass


@pytest.fixture
def fake_db(monkeypatch, tmp_path):
    calls = []

    def fake_conn():
        calls.append(True)
        return DummyConn()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    (tmp_path / "databases").mkdir()
    monkeypatch.setattr(database_utils, "get_validated_production_db_connection", lambda: fake_conn())
    monkeypatch.setattr(optimize_to_100_percent, "get_validated_production_db_connection", lambda: fake_conn())
    monkeypatch.setattr(security_compliance_enhancer, "get_validated_production_db_connection", lambda: fake_conn())
    return calls


def test_optimize_calls_db_first(fake_db, monkeypatch):
    monkeypatch.setattr(optimize_to_100_percent, "enhance_database_architecture", lambda: 100.0)
    monkeypatch.setattr(optimize_to_100_percent, "enhance_script_repository", lambda: 100.0)
    monkeypatch.setattr(optimize_to_100_percent, "enhance_copilot_integration", lambda: 100.0)
    monkeypatch.setattr(optimize_to_100_percent, "enhance_self_healing_system", lambda: 100.0)
    monkeypatch.setattr(optimize_to_100_percent, "enhance_disaster_recovery", lambda: 100.0)
    monkeypatch.setattr(optimize_to_100_percent, "finalize_100_percent_achievement", lambda: None)

    optimize_to_100_percent.optimize_to_100_percent()
    assert len(fake_db) > 0


def test_security_enhancer_calls_db_first(fake_db, monkeypatch):
    enhancer = security_compliance_enhancer.SecurityComplianceEnhancer(str(Path.cwd()))
    monkeypatch.setattr(enhancer, "create_security_policy", lambda: True)
    monkeypatch.setattr(enhancer, "create_access_control_matrix", lambda: True)
    monkeypatch.setattr(enhancer, "create_security_audit_framework", lambda: True)
    monkeypatch.setattr(enhancer, "create_encryption_standards", lambda: True)
    monkeypatch.setattr(enhancer, "validate_security_implementation", lambda: {"security_score": 100.0})

    enhancer.run_security_enhancement()
    assert len(fake_db) > 0
