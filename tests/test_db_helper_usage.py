import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from scripts.optimization import optimize_to_100_percent as opt
from scripts.optimization import security_compliance_enhancer as sec
from utils import db_utils


@contextmanager
def _dummy_conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    db = tmp_path / "production.db"
    with sqlite3.connect(db) as conn:
        yield conn
def test_optimize_calls_db_helper(monkeypatch, tmp_path):
    called = {"flag": False}

    def fake_conn(db_name: str = "production.db"):
        called["flag"] = True
        return _dummy_conn(tmp_path)

    monkeypatch.setattr(db_utils, "get_validated_connection", fake_conn)

    def _noop() -> float:
        with db_utils.get_validated_connection():
            pass
        return 100.0

    monkeypatch.setattr(opt, "enhance_database_architecture", _noop)
    monkeypatch.setattr(opt, "enhance_script_repository", _noop)
    monkeypatch.setattr(opt, "enhance_copilot_integration", _noop)
    monkeypatch.setattr(opt, "enhance_self_healing_system", _noop)
    monkeypatch.setattr(opt, "enhance_disaster_recovery", _noop)

    result = opt.optimize_to_100_percent()
    assert called["flag"]
    assert result["final_readiness"] == 100.0


def test_security_enhancer_calls_db_helper(monkeypatch, tmp_path):
    called = {"flag": False}

    def fake_conn(db_name: str = "production.db"):
        called["flag"] = True
        return _dummy_conn(tmp_path)

    monkeypatch.setattr(db_utils, "get_validated_connection", fake_conn)
    enhancer = sec.SecurityComplianceEnhancer(workspace_path=str(tmp_path))
    enhancer.reports_dir.mkdir(exist_ok=True)

    def _noop() -> bool:
        with db_utils.get_validated_connection():
            pass
        return True

    monkeypatch.setattr(enhancer, "create_security_policy", _noop)
    monkeypatch.setattr(enhancer, "create_access_control_matrix", _noop)
    monkeypatch.setattr(enhancer, "create_security_audit_framework", _noop)
    monkeypatch.setattr(enhancer, "create_encryption_standards", _noop)
    monkeypatch.setattr(enhancer, "validate_security_implementation", lambda: {"security_score": 100.0})

    result = enhancer.run_security_enhancement()
    assert called["flag"]
    assert result["enterprise_ready"]
