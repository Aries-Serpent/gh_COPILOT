import logging
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
    assert not authentication.authenticate_user("alice", "secret", user_db, "user")
    assert authorization.has_role(["admin"], "admin")
    assert not authorization.has_role(["user"], "admin")


def test_encryption_roundtrip():
    data = b"hello"
    key = 42
    roles = ["crypto"]
    enc = encryption.xor_encrypt(data, key, roles)
    assert enc != data
    dec = encryption.xor_decrypt(enc, key, roles)
    assert dec == data
    with pytest.raises(PermissionError):
        encryption.xor_encrypt(data, key, roles=[])


def test_audit_and_quantum_security(caplog):
    caplog.set_level(logging.INFO)
    audit_logging.log_event("alice", "login", ["auditor"])
    assert "AUDIT" in caplog.text
    with pytest.raises(PermissionError):
        audit_logging.log_event("alice", "login", [])
    token = quantum_security.generate_quantum_token(["quantum"])
    assert isinstance(token, str) and len(token) == 32
    with pytest.raises(PermissionError):
        quantum_security.generate_quantum_token([])


def test_security_dual_copilot_hooks(monkeypatch):
    calls: list[list[object]] = []
    validator = SecondaryCopilotValidator()
    monkeypatch.setattr(
        validator, "validate_corrections", lambda items, primary_success=True: calls.append(items) or True
    )

    user_db = {"bob": {"password": "pw", "roles": ["user", "auditor", "crypto", "quantum"]}}
    authentication.authenticate_user("bob", "pw", user_db, validator=validator)
    authorization.has_role(["user"], "user", validator=validator)
    encryption.xor_encrypt(b"x", 1, ["crypto"], validator=validator)
    audit_logging.log_event("bob", "login", ["auditor"], validator=validator)
    quantum_security.generate_quantum_token(["quantum"], validator=validator)
    assert len(calls) == 5

