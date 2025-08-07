import logging
from flask import Flask, Response, g
import pytest

from secondary_copilot_validator import SecondaryCopilotValidator

from web_gui.security import (
    audit_logging,
    authentication,
    authorization,
    encryption,
    quantum_security,
)


def test_authentication_and_authorization():
    user_db = {"alice": {"password": "secret", "roles": ["admin"]}}
    assert authentication.authenticate_user("alice", "secret", user_db, "admin")
    assert not authentication.authenticate_user("alice", "wrong", user_db)
    assert authorization.has_role(["admin"], "admin")
    assert not authorization.has_role(["user"], "admin")


def test_authorization_decorator():
    app = Flask(__name__)

    with app.app_context():
        @authorization.requires_role("admin")
        def handler() -> Response:
            return Response("ok")

        g.current_roles = {"admin"}
        assert handler().status_code == 200
        g.current_roles = set()
        assert handler().status_code == 403


def test_encryption_roundtrip():
    data = b"hello"
    key = b"k"
    roles = ["crypto"]
    token = encryption.encrypt(data, key, roles)
    assert encryption.decrypt(token, key, roles) == data
    with pytest.raises(PermissionError):
        encryption.encrypt(data, key, roles=[])


def test_audit_and_quantum_security(caplog):
    caplog.set_level(logging.INFO)
    audit_logging.log_event("alice", "login", ["auditor"])
    assert "AUDIT alice: login" in caplog.text
    with pytest.raises(PermissionError):
        audit_logging.log_event("alice", "login", [])
    token = quantum_security.generate_quantum_token(["quantum"], length=8)
    assert isinstance(token, str) and len(token) == 16
    with pytest.raises(PermissionError):
        quantum_security.generate_quantum_token([])


def test_security_dual_copilot_hooks(monkeypatch):
    calls: list[list[object]] = []
    validator = SecondaryCopilotValidator()
    monkeypatch.setattr(
        validator, "validate_corrections", lambda items, primary_success=True: calls.append(list(items)) or True
    )

    user_db = {"bob": {"password": "pw", "roles": ["user", "auditor", "crypto", "quantum"]}}
    authentication.authenticate_user("bob", "pw", user_db, validator=validator)
    authorization.has_role(["user"], "user", validator=validator)
    encryption.encrypt(b"x", b"k", ["crypto"], validator=validator)
    audit_logging.log_event("bob", "login", ["auditor"], validator=validator)
    quantum_security.generate_quantum_token(["quantum"], validator=validator)
    assert len(calls) == 5

